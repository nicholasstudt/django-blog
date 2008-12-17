from django.db import models

# Create your models here.
class Entry(models.Model):
    pub_date = models.DateTimeField('date published')
    slug = models.SlugField(unique_for_date='pub_date')

    modified = models.DateTimeField('last modified')
    modified.editable = False
    modified.auto_now = True

    headline = models.CharField(max_length=250) 
    author = models.ForeignKey('Author')
    content = models.TextField(help_text='This is help text');
    tags = models.ManyToManyField('Tag')

    class Meta:
        verbose_name_plural = 'entries'

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
