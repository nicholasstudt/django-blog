# blog/rpc/metaweblog.py
# Carson Gee
# 2010 July 16
# http://carsongee.com
#
# Adapted from http://www.allyourpixel.com/post/metaweblog-38-django/
#
# Modifications made:
#    Added proper authentication and authorization.
#    Added newMediaObject implementation
#    Made the getCategories call right. The returned struct was
#    lacking  htmlUrl, and rssUrl
#    Added full Blogger 1.0 API and Moveable Type API
#    Added handling for blog clients like blogtk that don't
#    always keep their different APIs straight.
#
#  General questions, what to do with constructs
#  return blogs for a site, or include authors
#  
#

from django.contrib.sites.models import Site
from blog.models import Tag, Entry, Author, DRAFT, PUBLISHED
import datetime, time

from blog.rpc.xmlrpc import public, list_public_methods
from blog.rpc.decorators import authenticated
from blog.rpc.utils import *

from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
import os




# Blogger 1.0 API Methods
#
#
# Complete implementation except for the template methods


@public
@authenticated()
def blogger_getUserInfo(user, appkey):
    """
    Returns a struct with userid (string), firstname, lastname,
    nickname, e-mail, and url.
    """

    return { 'userid': str(user.username), 'firstname': user.first_name,
             'lastname': user.last_name, 'nickname': user.first_name, 
             'email': user.email, 'url': user.get_absolute_url() }


@public
@authenticated()
def blogger_getUsersBlogs(user, appkey):
    """
    an array of <struct>'s containing the ID (blogid), name
    (blogName), and URL (url) of each blog.  Returning one blog
    for each defined author.
    """


    site = Site.objects.get_current()
    blogs = []

    authors = Author.objects.all()
    for author in authors:
        blogs.append( { 
                'blogid': str(author.id),
                'blogName': author.name,
                'url': 'http://%s%s' % (site.domain, 
                                        reverse("author_index", 
                                                kwargs = {'author': author.ident })),
                })
    

    return blogs

@public
@authenticated(pos=2)
def blogger_getPost(user, appkey, postid):

    return blogger_entry_struct(Entry.objects.get(id=postid), user)

@public
@authenticated(pos=2)
def blogger_getRecentPosts(user, appkey, blogid, numberOfPosts):
    entries = Entry.objects.filter(author__id=blogid).order_by('-pub_date')[:numberOfPosts]

    return [blogger_entry_struct(entry, user) for entry in entries]

@public
@authenticated(pos=2, perm="blog.add_entry")
def blogger_newPost(user, appkey, blogid, content, publish):
    """
    Blogger doesn't support titles, so we will use the standard trick of
    searching for a <title></title> tag and using that for a title. Returns
    post id.
    """

    authorid = blogid
    if not authorid:
        authorid = Author.objects.all()[0].id
    title, body = blogger_split_content(content)

    pub_date = datetime.datetime.now()
    
    entry = Entry(headline = title,
                  slug = slugify(title),
                  content = body,
                  author_id = authorid,
                  pub_date = pub_date,
                  status = publish and PUBLISHED or DRAFT,)
    entry.save()
    # No tagging in this API...at least formally
    # setTags(entry, struct)
    entry.sites.add(Site.obects.get_current())

    return entry.id

@public
@authenticated(pos=2, perm="blog.change_entry")
def blogger_editPost(user, appkey, postid, content, publish):
    entry = Entry.objects.get(id=postid)

    headline, body = blogger_split_content(content)
    entry.headline = headline
    entry.content = body
    entry.status = publish and PUBLISHED or DRAFT


    # No tags in blogger API
    # setTags(entry, struct)

    entry.save()

    return True


@public
@authenticated(pos=2, perm="blog.delete_entry")
def blogger_deletePost(user, appkey, postid, publish):
    entry = Entry.objects.get(id=postid)
    entry.delete()
    return True

    


# metaWeblog Methods
#
#
# Complete implementation from http://www.xmlrpc.com/metaWeblogApi
# and including the Movable Type extensions.


@public
@authenticated()
def metaWeblog_getCategories(user, blogid):
    """
       I have added the MovableType extensions, that should only
       come from the struct from the mt.getCategoryList method because
       some clients don't differentiate based on method call.
    """
    tags = Tag.objects.all()

    categories = []
    for tag in tags:
        category = { 'description': tag.tag,
                     'htmlUrl': full_url(
                                   reverse('tag_list', kwargs={'ident': tag.tag }), 
                                   Site.objects.get_current()),
                     'rssUrl': full_url(
                                   reverse('feed_tags', kwargs={'tag': tag.tag }), 
                                   Site.objects.get_current()),
                     'categoryName': tag.tag,
                     'categoryId': str(tag.id)
                     }
        categories.append(category)

    return categories



@public
@authenticated()
def metaWeblog_getPost(user, postid):
    entry = Entry.objects.get(id=postid)
    return entry_struct(entry)

@public
@authenticated()
def metaWeblog_getRecentPosts(user, blogid, num_posts):
    entries = Entry.objects.filter(author__id=blogid).order_by('-pub_date')[:num_posts]
    return [entry_struct(entry) for entry in entries]

@public
@authenticated(perm="blog.add_entry")
def metaWeblog_newPost(user, blogid, struct, publish):



    # Check if we are getting a userid in the post,
    # if we are not, default to the first author entered...
    authorid = blogid
    if not authorid:
        authorid = Author.objects.all()[0].id

    pub_date = struct.get('dateCreated', None)
    if not pub_date:
        pub_date = datetime.datetime.now()
    else:
        # ISO 8601 time parsing is one of those things that sucks, and Python
        # doesn't have any decent way of handling the variety of formats
        # it may come in.  So, we make an effort to parse the most common
        # form, and then default to today if we can't figure it out correctly.
        try:
            pub_date = datetime.datetime.strptime( str(pub_date), "%Y%m%dT%H:%M:%S" )
        except ValueError:
            pub_date = datetime.datetime.now()
    

    content = struct['description']
    # todo - parse out technorati tags

    # Handle Movable Type extensions
    # We ignore pings, tb_ping_urls, keywords, and convert_breaks
    # If we get text_more we just append it to the content
    comments = struct.get('mt_allow_comments', None)
    if comments is not None:
        comments = bool(comments)
    else:
        # User default value
        comments = True
    
    abstract = struct.get('mt_excerpt', None)
    if abstract is None:
        abstract = ''
    
    footer = struct.get('mt_text_more', None)
    if footer is not None:
        content += footer


    entry = Entry(headline = struct['title'],
                  slug = slugify(struct['title']),
                  content = content,
                  author_id = authorid,
                  pub_date = pub_date,
                  comments = comments,
                  abstract = abstract,
                  status = publish and PUBLISHED or DRAFT,)

    # entry.prepopulate()
    entry.save()
    
    # Add any tags needed
    setTags(entry, struct.get('categories', None))
    # Add site by using blogid
    entry.sites.add(Site.objects.get_current())

    return entry.id

@public
@authenticated(perm="blog.change_entry")
def metaWeblog_editPost(user, postid, struct, publish):
    entry = Entry.objects.get(id=postid)

    headline = struct.get('title', None)
    if headline is not None:
        entry.headline = headline
    
    content = struct.get('description', None)        
    if content is not None:
        entry.content = content
        # todo - parse out technorati tags

    # Handle Movable Type Extensions
    comments = struct.get('mt_allow_comments', None)
    if comments is not None:
        entry.comments = bool(comments)
    
    abstract = struct.get('mt_excerpt', None)
    if abstract is not None:
        entry.abstract = abstract

    footer = struct.get('mt_text_more', None)
    if footer is not None:
        entry.content += footer

    entry.status = publish and PUBLISHED or DRAFT

    setTags(entry, struct.get('categories', None))


    entry.save()

    return True

@public
@authenticated(perm="blog.change_entry")
def metaWeblog_newMediaObject(user, blogid, struct):
    """
       By default, uploads to settings.MEDIA_ROOT/[datestamp]_[orig_name].
       
       If settings.BLOG_RPC_UPLOAD_PATH is set to a tuple, I will run strftime
       against it, and append the passed in filename to the end of the time
       format string. The tuple should be ( file_path, url_path )

       If you set settings.BLOG_RPC_UPLOAD_PATH as a python callable,
       I will call it with **kwargs set at {user: django user object,
       author_id: blog author id, name: file name to upload } which must
       return a tuple that is a valid path and URL to that path.
    """
    
    # The input struct must contain at least three elements, name,
    # type and bits. returns struct, which must contain at least one
    # element, url

    
    mime = struct.get('type', None)
    bits = struct['bits']
    name = os.path.basename(struct['name'])


    if not settings.MEDIA_URL.find('http') == 0:
        prefix = "%s%s" % ("http://", Site.objects.get_current().domain)
    else:
        prefix = ''

    default_string = False
    upload_path = None

    try:
        upload_path = settings.BLOG_RPC_UPLOAD_PATH
    except:
        path_extension = "%s-%s" % (time.strftime("%Y%m%d", time.localtime()),
                                    name)
        file_path = "%s/%s" % (settings.MEDIA_ROOT, path_extension)
        url_path =  "%s%s%s" % (prefix, settings.MEDIA_URL, path_extension)
        default_string = True

    if callable(upload_path):
        file_path, url_path = upload_path(user = user,
                                  author_id = blogid,
                                  name = name )
    elif not default_string:
        file_path, url_path = ("%s%s" % (time.strftime(x, time.localtime()), name) for x in upload_path)
    
    # Make sure whatever path we got exists, and create it if it doesn't
    path = os.path.normpath(file_path)
    path_dir = os.path.split(path)[0]

    # If we don't have permissions or another OSError is raised, let
    # it go, we want the call to fail. the xmlrpc will return the
    # exception in the response struct.
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
    
    f = open(path,'w')
    f.write("%s" % bits)
    f.close()
   
    return { 'url': url_path }



# MovableType API
#
#
# Implementation the same as done with http://txp.kusor.com/rpc-api/


@public
def mt_supportedMethods():

    """
       Register an empty method name for this.  Within the xmlrpc.py,
       I intercept calls to this method, and return system.listMethods().

       While technical, I don't need to register it.  I am keeping it here
       for documentation purposes
    """

    return None


@public
def mt_supportedTextFilters():
    """
    We currently do not implement any text filters.  We could if it
    ever comes up.
    """

    return [ {'key': '0', 'label': "Leave Text Untouched" }, ]

@public
@authenticated()
def mt_getCategoryList(user, blogid):
    """
    Similar to the metaWeblog getCategories, but a different struct is returned.
    """
    
    tags = Tag.objects.all()

    categories = []
    for tag in tags:
        category = { 
                     'categoryName': tag.tag,
                     'categoryId': str(tag.id)
                     }
        categories.append(category)
    
    return categories
    
@public
@authenticated()
def mt_getPostCategories(user, postid):
    """
    isPrimary doesn't really make sense for this app, so I have hard
    set it to True.
    """

    entry = Entry.objects.get(id=int(postid))
    tags = entry.tags.all()

    categories = []
    for tag in tags:
        category = { 
                     'categoryName': tag.tag,
                     'categoryId': str(tag.id),
                     'isPrimary': True
                     }
        categories.append(category)
    
    return categories
    

@public
@authenticated(perm="blog.change_entry")
def mt_setPostCategories(user, postid, categories):
    """
    This interface doesn't support adding new categories,
    and only passes in categoryIds.
    So we will look up each one, and if we fail to find one,
    we will just ignore that tag.
    """

    # Build list of tag names for setTags function in utils.
    tags = []
    for struct in categories:
        try:
            catId = int(struct['categoryId'])
            tag = Tag.objects.get(id=catId)
            tags.append(tag.tag)
        except:
            pass

    entry = Entry.objects.get(id=int(postid))
    setTags(entry, tags)
    
    return True

    
