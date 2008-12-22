from django.db import models
from django.utils.translation import ugettext_lazy as _

from blog.managers import PublishedManager

# Create your models here.
class Entry(models.Model):
    """Entry Model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Publish')),
    )

    pub_date = models.DateTimeField(_('date published'))
    slug = models.SlugField(_('slug'),unique_for_date='pub_date')
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    comments = models.BooleanField(_('allow comments'), default=True)

    modified = models.DateTimeField(_('last modified'))
    modified.editable = False
    modified.auto_now = True

    headline = models.CharField(max_length=250) 
    author = models.ForeignKey('Author')
    content = models.TextField(help_text='This is help text');
    tags = models.ManyToManyField('Tag')

    objects = PublishedManager()

    class Meta:
        verbose_name_plural = _('entries')
        ordering = ('-pub_date',)

    def __unicode__(self):
        return( u'%s' % self.headline )

    @models.permalink
    def get_absolute_url(self):
        return ('entry_detail', (), {
                'year': self.pub_date.year,
                'month': self.pub_date.month,
                'day': self.pub_date.day,
                'slug': self.slug
        })

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
   
    @models.permalink
    def get_absolute_url(self):
        return('author_detail', (), { 'ident': self.ident })

class Tag(models.Model):
    tag = models.SlugField(max_length=250)
    #count = models.IntegerField()
    # Do I need the count here ?

    def __unicode__(self):
        return( u'%s' % self.tag )
