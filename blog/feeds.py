from django.contrib.syndication.feeds import Feed
from django.contrib.sites.models import Site
from django.contrib.comments.feeds import LatestCommentFeed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from blog.models import Entry

class LatestEntries(Feed):
    _site = Site.objects.get_current()
    title = '%s feed' % _site.name
    description = '%s posts feed.' % _site.name

    def link(self):
        return reverse('entry_index')

    def item_pubdate(self, obj):
        return obj.pub_date

    def items(self):
        return Entry.objects.published()[:10]

class LatestEntriesByTag(Feed):
    _site = Site.objects.get_current()

    def get_object(self, request, tag):
        return get_object_or_404(Tag, slug=tag)

    def title(self, obj):
        return '%s feed: %s' % [_site.name, obj.tag]

    def description(self, obj):
        return '%s posts feed for %s' % [_site.name, obj.tag]

    def link(self, obj):
        return reverse('tag_list', ident=obj.tag)

    def item_pubdate(self, obj):
        return obj.pub_date

    def items(self, obj):
        return Entry.objects.published()[:10]

class LatestComments(LatestCommentFeed):
    pass
    # Accept all of the contrib.comments defaults.
