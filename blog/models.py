import calendar
import datetime

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.db.models import Manager

from django.contrib.comments.moderation import CommentModerator, moderator

DRAFT = 1
PUBLISHED = 2

class EntryPublishedManager(Manager):
    """Returns published posts that are not in the future.""" 
    def published_bymonth(self, year, month, **kwargs):
        "Get all items published in a given month"
        gte = datetime.date(year, month, 1)
        lte = datetime.date(year, month, calendar.monthrange(year, month)[1])

        if lte >= datetime.date.today(): # Dont' show the future.
            lte = datetime.datetime.now()

        return self.get_query_set().filter(status__gte=PUBLISHED, pub_date__gte=gte, pub_date__lte=lte, sites__id__exact=settings.SITE_ID, **kwargs)

    def published(self, **kwargs):
        # If pub_date__lte is not in kwargs add it.
        return self.get_query_set().filter(status__gte=PUBLISHED, pub_date__lte=datetime.datetime.now(), sites__id__exact=settings.SITE_ID, **kwargs)

    def all_published(self, **kwargs):
        # If pub_date__lte is not in kwargs add it.
        return self.get_query_set().filter(sites__id__exact=settings.SITE_ID, **kwargs)


# Create your models here.
class Entry(models.Model):
    """Entry Model."""
    STATUS_CHOICES = (
        (DRAFT, _('Draft')),
        (PUBLISHED, _('Publish')),
    )

    try: 
        sid = settings.SITE_ID 
    except AttributeError: 
        from django.core.exceptions import ImproperlyConfigured 
        raise ImproperlyConfigured("You're using the Django \"sites framework\" without having set the SITE_ID setting. Create a site in your database and set the SITE_ID setting to fix this error.") 

    slug = models.SlugField(_('slug'),unique_for_date='pub_date')
    pub_date = models.DateTimeField(_('date published'))
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=PUBLISHED)
    comments = models.BooleanField(_('allow comments'), default=True)

    modified = models.DateTimeField(_('last modified'), editable=False, auto_now=True)

    headline = models.CharField(max_length=250) 
    author = models.ForeignKey('Author')
    abstract = models.TextField(help_text=_('Entry Abstract'), blank=True);
    content = models.TextField(help_text=_('Entry Content'));
    sites = models.ManyToManyField(Site, default=(sid,))
    tags = models.ManyToManyField('Tag', blank=True)

    objects = EntryPublishedManager()

    class Meta:
        verbose_name_plural = _('entries')
        ordering = ('-pub_date',)

    def __unicode__(self):
        return( u'%s' % self.headline )

    def is_published(self):
        return(self.status == PUBLISHED)

    def can_comment(self):
        try: 
            if (datetime.datetime.now() - self.pub_date).days >= int(settings.BLOG_COMMENTS_CLOSE_AFTER):
                return False
        except (AttributeError, ValueError):
            pass

        return(self.comments)

    def get_absolute_url(self):
        return('entry_detail', (), {
                'year': self.pub_date.year,
                'month': self.pub_date.strftime('%m'),
                'day': self.pub_date.day,
                'slug': self.slug
        })
    get_absolute_url = models.permalink(get_absolute_url)

    def get_previous_post(self):
        return(self.get_previous_by_pub_date(status__gte=PUBLISHED, sites__id__exact=settings.SITE_ID))
                
    def get_next_post(self):
        return(self.get_next_by_pub_date(status__gte=PUBLISHED, sites__id__exact=settings.SITE_ID))


class EntryModerator(CommentModerator):
    enable_field = 'comments' 
    
    try: 
        if settings.BLOG_COMMENTS_EMAIL_NOTIFICATION:
            try: 
                email_notification = settings.BLOG_COMMENTS_EMAIL_NOTIFICATION
            except ValueError:
                pass
    except AttributeError:
        pass

    try: 
        if settings.BLOG_COMMENTS_CLOSE_AFTER:
            try: 
                auto_close_field = 'pub_date'    
                close_after = settings.BLOG_COMMENTS_CLOSE_AFTER
            except ValueError:
                pass
    except AttributeError:
        pass

    try: 
        if settings.BLOG_COMMENTS_MODERATE_AFTER:
            try: 
                auto_moderate_field = 'pub_date'    
                moderate_after = settings.BLOG_COMMENTS_MODERATE_AFTER
            except ValueError:
                pass
    except AttributeError:
        pass

moderator.register(Entry, EntryModerator)

class Author(models.Model):
    ident = models.SlugField()
    name = models.CharField(max_length=250)
    email = models.EmailField()
    content = models.TextField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return(u'%s' % self.name)
   
    def get_absolute_url(self):
        return('author_detail', (), { 'ident': self.ident })
    get_absolute_url = models.permalink(get_absolute_url)

class Tag(models.Model):
    tag = models.SlugField(max_length=250)
    #count = models.IntegerField()
    # Do I need the count here ?

    class Meta:
        ordering = ('tag',)

    def __unicode__(self):
        return( u'%s' % self.tag )

    def get_absolute_url(self):
        return('tag_list', (), { 'ident': self.tag })
    get_absolute_url = models.permalink(get_absolute_url)

