from django.db import models
from django.utils.translation import ugettext_lazy as _

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

    class Meta:
        verbose_name_plural = _('entries')

    def __unicode__(self):
        return self.headline

class Author(models.Model):
    ident = models.SlugField()
    name = models.CharField(max_length=250)
    email = models.EmailField()
    content = models.TextField()

    def __unicode__(self):
        return self.name

class Tag(models.Model):
    tag = models.SlugField(max_length=250)

    def __unicode__(self):
        return self.tag
