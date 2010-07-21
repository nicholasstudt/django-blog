from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site
from django.contrib.comments.feeds import LatestCommentFeed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from blog.models import Entry, Tag

class LatestEntriesFeed(Feed):
    _site = Site.objects.get_current()
    title = '%s feed' % _site.name
    description = '%s posts feed.' % _site.name
    title_template = 'feeds/latest/title.html'
    description_template = 'feeds/latest/description.html'

    def items(self):
        return Entry.objects.published()[:10]

    def item_pubdate(self, obj):
        return obj.pub_date

    def link(self):
        return reverse('entry_index')


class LatestEntriesByTag(Feed):
    _site = Site.objects.get_current()
    title_template = 'feeds/tags/title.html'
    description_template = 'feeds/tags/description.html'

    def get_object(self, request, tag):
        return get_object_or_404(Tag, tag=tag)

    def title(self, obj):
        return '%s feed: %s' % (self._site.name, obj.tag)

    def description(self, obj):
        return '%s posts feed for %s' % (self._site.name, obj.tag)

    def link(self, obj):
        return reverse('tag_list', args=[obj.tag])

    def item_pubdate(self, obj):
        return obj.pub_date

    def items(self, obj):
        return Entry.objects.published()[:10]

class LatestComments(LatestCommentFeed):
    # Accept all of the contrib.comments defaults.
    pass
