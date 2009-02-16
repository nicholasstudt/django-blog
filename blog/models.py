from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from blog.managers import PublishedManager

# Create your models here.
class Entry(models.Model):
    """Entry Model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Publish')),
    )

    try: 
        sid = settings.SITE_ID 
    except AttributeError: 
        from django.core.exceptions import ImproperlyConfigured 
        raise ImproperlyConfigured("You're using the Django \"sites framework\" without having set the SITE_ID setting. Create a site in your database and set the SITE_ID setting to fix this error.") 

    pub_date = models.DateTimeField(_('date published'))
    slug = models.SlugField(_('slug'),unique_for_date='pub_date')
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    comments = models.BooleanField(_('allow comments'), default=True)

    modified = models.DateTimeField(_('last modified'), editable=False, auto_now=True)

    headline = models.CharField(max_length=250) 
    author = models.ForeignKey('Author')
    abstract = models.TextField(help_text=_('Entry Abstract'), blank=True);
    content = models.TextField(help_text=_('Entry Content'));
    sites = models.ManyToManyField(Site, default=(sid,))
    tags = models.ManyToManyField('Tag', blank=True)

    objects = PublishedManager()

    class Meta:
        verbose_name_plural = _('entries')
        ordering = ('-pub_date',)

    def __unicode__(self):
        return( u'%s' % self.headline )

    def get_absolute_url(self):
        return ('entry_detail', (), {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime('%m'),
                'day': self.pub_date.day,
                'slug': self.slug
        })
    get_absolute_url = models.permalink(get_absolute_url)


    def get_previous_post(self):
        return( self.get_previous_by_pub_date(status__gte=2) )
                
    def get_next_post(self):
        return( self.get_next_by_pub_date(status__gte=2) )


class Author(models.Model):
    ident = models.SlugField()
    name = models.CharField(max_length=250)
    email = models.EmailField()
    content = models.TextField()

    def __unicode__(self):
        return( u'%s' % self.name )
   
    def get_absolute_url(self):
        return('author_detail', (), { 'ident': self.ident })
    get_absolute_url = models.permalink(get_absolute_url)

class Tag(models.Model):
    tag = models.SlugField(max_length=250)
    #count = models.IntegerField()
    # Do I need the count here ?

    def __unicode__(self):
        return( u'%s' % self.tag )

    def get_absolute_url(self):
        return('tag_list', (), { 'ident': self.tag })
    get_absolute_url = models.permalink(get_absolute_url)

