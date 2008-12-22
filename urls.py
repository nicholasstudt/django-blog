from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',

    # /article/<section>/<date "YYYY-MM-DD">/<ident> -> One article
    # /YYYY-MM-DD/slug
    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 
        'entry_detail', 
        name="entry_detail"),

    # /archive/<section>/<date-part "YYYY-MM-DD">
    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/$',
        'entry_archive_day', 
        name="archive_day"),

    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})/$', 
        'entry_archive_month',
        name="archive_month"),

    url(r'^(?P<year>\d{4})/$', 
        'entry_archive_year',
        name="archive_year"),

    # /author/<author ident>
    url(r'^author/(?P<ident>[-\w]+)/$', 
        'author_detail', 
        name="author_detail"),

    # /search
    url(r'^search/$', 
        'entry_search',
        name="entry_search"),

    url(r'^comments/', include('django.contrib.comments.urls')),

    url(r'^$', 
        'entry_list',
        name="entry_index"),
)
