#!/usr/bin/python
import os
import string
import sys
import psycopg2
import psycopg2.extras

from optparse import OptionParser

# python blog-sqlmigrate.py --dsn="dbname='devel' user='apache'" devel
# python local_apps/blog/bin/blog-sqlmigrate.py --dsn="dbname='photodwarf' user='apache'" devel

def main():
    usage = "usage: %prog [options] project"
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=True,
                    help="make lots of noise [default]")
    parser.add_option("-s", "--site", default=1, help="Sites ID")
    parser.add_option("-d", "--dsn", metavar="DSN",
                    help="Database Source Name")
    parser.add_option("-p", "--path", help="File URI" )

    (options, args) = parser.parse_args()

    if len(args) != 1:
        sys.stderr.write("Type '%s --help' for usage.\n" % sys.argv[0])
        sys.exit(2)

    if not options.dsn:
        sys.stderr.write("Type '%s --help' for usage.\n" % sys.argv[0])
        sys.exit(2)
    
    # Allows us to import the models
    os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings" % args[0]

    # Import in the models
    try:
        from blog.models import Entry, Author, Tag
        from django.contrib.sites.models import Site
        from django.contrib.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
    except ImportError, error:
        sys.stderr.write("%s\n" % error)
        sys.exit(1)

    # Connect to the database. 
    try: 
        connection = psycopg2.connect(options.dsn)
    except psycopg2.OperationalError, error:
        sys.stderr.write("DSN Error %s" % error)
        sys.exit(1)

#    if options.verbose:
#        print "Options: %s" % options
#        print "Args: %s" % args

  
    # Import Authors
    c = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c2 = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT ident, name, email, photo, bio FROM bg_authors")

    for row in c.fetchall():
    
        if row['photo']:
            if options.path: 
                photo = string.join( (options.path.rstrip("/"), row['photo']), 
                                     sep="/")
            else:
                photo = row['photo']

            content = """<img src="%s" alt="%s" />\n%s""" % ( photo, row['name'], row['bio'] )
        else:
            content = row['bio']

        a = Author(ident=row['ident'], name=row['name'], email=row['email'], content=content)
        a.save()

    # Import Categories as Tags
    c.execute("SELECT ident FROM bg_categories")

    for row in c.fetchall():
        t = Tag(tag=row['ident'])
        t.save()
   
    # Import Articles
    c.execute("SELECT a.id, t.published, a.ident, a.a_options, a.topic, a.pub_date, a.modified, a.summary, a.content, w.ident as author_ident FROM bg_articles as a, bg_article_type as t, bg_authors as w WHERE t.id = a.bg_article_type_id AND a.bg_author_id = w.id ")

    for row in c.fetchall():

        status = 1
        if row['published']:
            status = 2

        comments = False
        if row['a_options'] > 0:
            comments = True

        e = Entry(pub_date=row['pub_date'], slug=row['ident'],
                    status=status,
                    comments=comments,
                    modified=row['modified'],
                    headline=row['topic'],
                    author=Author.objects.get(ident=row['author_ident']),
                    abstract=row['summary'],
                    content=row['content'],
                    )
        e.save()

        # Add the site to the Entry.
        e.sites.add(Site.objects.get(id=options.site))
        e.save()
        
        # Import Article Cateogies as Tags
        c2.execute("SELECT c.ident FROM bg_article_categories as a, bg_categories as c WHERE c.id = a.bg_category_id AND a.bg_article_id = %s" % row['id'])

        for trow in c2.fetchall():
            e.tags.add(Tag.objects.get(tag=trow['ident']))

        e.save()

        # Import Article Comments.
        c2.execute("SELECT approved, created, post_ip, name, email, url, content FROM bg_article_comments WHERE bg_article_id = %s" % row['id'] )

        for trow in c2.fetchall():
            c = Comment(ip_address=trow['post_ip'],
                        user_name=trow['name'],
                        user_email=trow['email'], 
                        user_url=trow['url'],
                        submit_date=trow['created'] ,
                        comment=trow['content'],
                        content_type=ContentType.objects.get(name='entry'),
                        object_pk=e.id,
                        site=Site.objects.get(id=options.site))
            c.save()
    
 
if __name__ == "__main__":
    main()
