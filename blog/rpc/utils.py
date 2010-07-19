import urlparse
from xmlrpclib import DateTime
from blog.models import Tag, Entry, Author, DRAFT, PUBLISHED
from django import template
import datetime
import re


def full_url(url, site):
    return urlparse.urljoin("http://%s" % site.domain, url)

def format_date(d):
    if not d: return None
    return DateTime(d.strftime("%Y%m%dT%H:%M:%S"))


def blogger_split_content(content):

    # Non greedy first title search
    title_regex = re.compile(r'.*?<title>(?P<title>.+?)</title>.*', re.DOTALL)
    m = title_regex.search(content)
    if m:
        title = m.groups('title')[0]
        body = re.sub( re.compile(r'<title>.*?</title>', re.DOTALL), '', content, 1)
    else:
        # Make the first line the title
        title, body = content.split('\n', 1)
    
    return (title, body)
    

def blogger_entry_struct(entry, user):

    return  {
        'postid': str(entry.id),
        'userid': str(user.id),
        'dateCreated': format_date(entry.pub_date),
        'content': "<title>%s</title>\n%s" % (entry.headline, entry.content),
        }
    

# example... this is what wordpress returns:
# {'permaLink': 'http://gabbas.wordpress.com/2006/05/09/hello-world/',
#  'description': 'Welcome to <a href="http://wordpress.com/">Wordpress.com</a>. This is your first post. Edit or delete it and start blogging!',
#  'title': 'Hello world!',
#  'mt_excerpt': '',
#  'userid': '217209',
#  'dateCreated': <DateTime u'20060509T16:24:39' at 2c7580>,
#  'link': 'http://gabbas.wordpress.com/2006/05/09/hello-world/',
#  'mt_text_more': '',
#  'mt_allow_comments': 1,
#  'postid': '1',
#  'categories': ['Uncategorized'],
#  'mt_allow_pings': 1}

def entry_struct(entry):

    """
       Formats the post entry for metaweblog.  

       Caveats: 
       Defaults to using the first site available for an
       entry that belongs multiple sites
    """
    
    link = full_url(entry.get_absolute_url(), entry.sites.all()[0])
    categories = entry.tags.all()
    struct = {
        'postid': str(entry.id),
        'title': entry.headline,
        'link': link,
        'permaLink': link,
        'description': entry.content,
        'categories': [c.tag for c in categories],
        'userid': str(entry.author.id),
        'dateCreated': format_date(entry.pub_date),
        'mt_excerpt': entry.abstract,
        'mt_text_more': '',
        'mt_allow_comments': entry.comments,
        'mt_allow_pings': 0,
        'mt_tb_ping_urls': '',
        'mt_convert_breaks': 0,
        'mt_keywords': '',
        }
    return struct

def getTagsFromMT(tags): 

    tag_list = []
    for struct in tags:
        try:
            catId = int(struct['categoryId'])
            tag = Tag.objects.get(id=catId)
            tag_list.append(tag.tag)
        except:
            pass
    return tag_list

def setTags(entry, tags):
    
    if tags is None:
        entry.tags = []
    else:
        try:
            # Check if we got a movable type style category array of structs
            if type(tags[0]) == dict:
                # We have a MT style list of IDs.
                tags = getTagsFromMT(tags)
        except:
            pass
        # Create any tags that don't exist yet, and then add them to the entry
        for tag in tags:
            if len(Tag.objects.filter(tag__iexact=tag)) == 0:
                new_tag = Tag()
                new_tag.tag = tag
                new_tag.save()
        entry.tags = [Tag.objects.get(tag__iexact=tag) for tag in tags]
    
