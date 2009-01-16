#!/usr/bin/python
import os
import string
import sys
import psycopg2
import psycopg2.extras

from optparse import OptionParser

# python blog-sqlmigrate.py --dsn="dbname='devel' user='apache'" devel

def main():
    usage = "usage: %prog [options] project"
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=True,
                    help="make lots of noise [default]")
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
    except ImportError, error:
        sys.stderr.write("%s\n" % error)
        sys.exit(1)

    # Connect to the database. 
    try: 
        connection = psycopg2.connect(options.dsn)
    except psycopg2.OperationalError, error:
        sys.stderr.write("DSN Error %s" % error)
        sys.exit(1)

    if options.verbose:
        print "Options: %s" % options
        print "Args: %s" % args

  
    # Import Authors
    c = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
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
    c.execute("SELECT ident FROM bg_categories")
        # Assume everyone goes into settings.SITE_ID
        # Import Article Comments.
    
 
if __name__ == "__main__":
    main()
