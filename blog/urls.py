from django.conf.urls.defaults import *
from blog.feeds import LatestEntriesByTag, LatestEntries, LatestComments

feeds = {   
    'latest': LatestEntries,
    'tags': LatestEntriesByTag,
    'comments': LatestComments,
}

urlpatterns = patterns('',
    # /article/<section>/<date "YYYY-MM-DD">/<ident> -> One article
    # /YYYY-MM-DD/slug (allow anything in as slug, for old idents) 
    # (?P<slug?>[-\w]+) What slug should be...
    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<slug>.*[-\w]+)/?$',
        'blog.views.entry_detail', 
        name="entry_detail"),

    # /archive/<section>/<date-part "YYYY-MM-DD">
    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/?$',
        'blog.views.entry_archive_day', 
        name="archive_day"),

    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})/?$', 
        'blog.views.entry_archive_month',
        name="archive_month"),

    url(r'^(?P<year>\d{4})/?$', 
        'blog.views.entry_archive_year',
        name="archive_year"),

    url(r'^tags/(?P<ident>[-\w]+)/?$', 
        'blog.views.tag_list', 
        name="tag_list"),

    # /author/<author ident>
    url(r'^author/(?P<ident>[-\w]+)/?$', 
        'blog.views.author_detail', 
        name="author_detail"),

    url(r'^author/?$', 
        'blog.views.author_list', 
        name="author_list"),

    # /search
    url(r'^search/?$', 
        'blog.views.entry_search',
        name="entry_search"),

    # /feeds/tags, /feeds/latest,
    url(r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed',
            {'feed_dict': feeds}),

    url(r'^comments/', include('django.contrib.comments.urls')),

    url(r'^$', 'blog.views.entry_list', name="entry_index"),
)

