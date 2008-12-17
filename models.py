from django.db import models

# Create your models here.
class Entry(models.Model):
    slug = models.SlugField(unique_for_date='pub_date')
    pub_date = models.DateTimeField('date published')
    modified = models.DateTimeField('last modified')
    headline = models.CharField(max_length=250) 
    author = models.ForeignKey('Author')
    content = models.TextField();
    tags = models.ManyToManyField('Tags')

    def __unicode__(self):
        return self.headline

class Author(models.Model):
    ident = models.SlugField()
    name = models.CharField(max_length=250)
    email = models.EmailField()
    content = models.TextField()

    def __unicode__(self):
        return self.name

class Tags(models.Model):
    tag = models.SlugField(max_length=250)

    def __unicode__(self):
        return self.tag
