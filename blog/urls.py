from django.conf.urls.defaults import *
from blog.feeds import LatestEntriesByTag, LatestEntriesFeed, LatestComments
from blog.views import EntryList, TagList, EntryLatest, EntryDetail, EntrySearch, EntryArchiveYear, EntryArchiveMonth, EntryArchiveDay, AuthorDetail, AuthorList

urlpatterns = patterns('',
    # /YYYY-MM-DD/slug (allow anything in as slug, for old idents) 
    # (?P<slug?>[-\w]+) What slug should be...
    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<slug>.*[-\w]+)/?$',
        EntryDetail.as_view(), 
        name="entry_detail"),

    # /<date-part "YYYY-MM-DD">
    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/?$',
        EntryArchiveDay.as_view(), 
        name="archive_day"),

    url(r'^(?P<year>\d{4})-(?P<month>\d{1,2})/?$', 
        EntryArchiveMonth.as_view(),
        name="archive_month"),

    url(r'^(?P<year>\d{4})/?$', 
        EntryArchiveYear.as_view(),
        name="archive_year"),

    url(r'^tags/(?P<ident>[-\w]+)/?$', 
        TagList.as_view(),
        name="tag_list"),

    # /author/<author ident>
    url(r'^author/(?P<ident>[-\w]+)/?$', 
        AuthorDetail.as_view(),
        name="author_detail"),

    url(r'^author/?$', 
        AuthorList.as_view(),
        name="author_list"),

    # /search
    url(r'^search/?$', EntrySearch.as_view(),
        name="entry_search"),

    # /feeds/tags, /feeds/latest,
    url(r'^feeds/latest/?$', LatestEntriesFeed(), 
        name='feed_latest'),

    url(r'^feeds/tags/(?P<tag>[-\w]+)/?$', LatestEntriesByTag(), 
        name='feed_tags' ),

    url(r'^feeds/comments/?$', LatestComments(), name='feed_comments' ),

    url(r'^comments/', include('django.contrib.comments.urls')),
    
    url(r'^latest/?$', EntryLatest.as_view(), name="entry_latest"),

    # New RPC handling
    url(r'^rpc/?$', 'blog.rpc.xmlrpc.view', {'module': 'blog.rpc.metaweblog' }),

    url(r'^(?P<author>[-\w]+)/?$', EntryList.as_view(), 
        name="author_index"),

    url(r'^$', EntryList.as_view(), name="entry_index"),
)
