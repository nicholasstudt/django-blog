from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import TemplateSyntaxError
from django.conf import settings
from django.db import models

Tag = models.get_model('blog', 'tag')
Entry = models.get_model('blog', 'entry')
Author = models.get_model('blog', 'author')

register = template.Library()

class EntryList(template.Node):
    def __init__(self, var_name, kind='month', limit=None, author=None):
        self.var_name = var_name
        self.kind = kind
        self.limit = limit 
        self.author = author 

    def render(self, context):
        author = None

        if self.author:
            try: 
                author = Author.objects.get(ident=self.author)
            except ObjectDoesNotExist: 
                pass

        if author:
            list = Entry.objects.published(author=author).dates('pub_date', self.kind, order='DESC')
        else: 
            list = Entry.objects.published().dates('pub_date', self.kind, 
                                               order='DESC')

        if self.limit:
            context[self.var_name] = list[:self.limit]
        else:
            context[self.var_name] = list
        return ''

class TagList(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = Tag.objects.all()
        return ''

def tag_list_as(parser, token):
    """
    List all of the tags.

    Example::

        {% tag_list_as [name] %}
        
        {% load blog %}

        {% tag_list_as tags %} 
        <ul>
            {% for tag in tags %}
                <li><a href="{% url tag_list tag %}">{{ tag }}</a></li>
            {% endfor %}
        </ul>
    """

    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "'%s' tag requires a single argument: the context name to populate" % bits[0]
    return TagList(bits[1])
tag_list_as = register.tag(tag_list_as)

def entry_archive(parser, token):
    """
    List all of the tags.

    Example::

        {% entry_archive [name] <count|all>:<year|month|day> [author_ident] %}
        
        {% load blog %}

        {% entry_archive entries all:month author_ident_here %} 
        <ul>
            {% for entry in entries %}
                <li><a href="{% url tag_list tag %}">{{ entry.name }}</a></li>
            {% endfor %}
        </ul>

    """
    limit = None
    author = None
    type = 'month'
    bits = token.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError, "'%s' tag requires at least the context name to populate" % bits[0]
    
    if len(bits) >= 3:
        (limit, type) = bits[2].split(':') 
        try: 
            limit = int(limit)
        except ValueError: 
            limit = None

    if len(bits) == 4:
        author = bits[3]

    return EntryList(bits[1], type, limit, author)
entry_archive = register.tag(entry_archive)
