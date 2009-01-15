from django.contrib.syndication.feeds import Feed
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
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
    title = '%s feed' % _site.name
    description = '%s posts feed.' % _site.name

    def link(self):
        return reverse('entry_index')

    def item_pubdate(self, obj):
        return obj.pub_date

    def items(self):
        return Entry.objects.published()[:10]
