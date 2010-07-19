import calendar
import datetime

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

class Calendar(template.Node):
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
    Listing of of years, months, or days that have entries.

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

def month_calendar(parser, token):
    """
    Create a calendar of a month with the days that have entries linked
    to that day in the archive.

    Example::

        {% month_calendar <year> <month> [author_ident] %}
        
        {% load blog %}

        {% month_calendar 2010 11 author_ident_here %} 

    """
    
    author = None
    year = datetime.date.today().year
    month = datetime.date.today().month

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

    return Calendar(bits[1], type, limit, author)
entry_archive = register.tag(entry_archive)

def month_cal(parser, token):
    year=datetime.date.today().year
    month=datetime.date.today().month

    # Fix this to just use calendar.* for all math.

    first_day_of_month = datetime.date(year, month, 1)
    last_day_of_month = calendar.monthrange(year, month)
    first_day_of_calendar = first_day_of_month - datetime.timedelta(first_day_of_month.weekday())

    last_day_of_calendar = datetime.date(year,month,last_day_of_month[1]) + datetime.timedelta(7 - calendar.weekday(year,month,last_day_of_month[1]))

    return last_day_of_calendar

    event_list = Entry.objects.published(pub_date__gte=first_day_of_calendar, pub_date__lte=last_day_of_calendar)

    month_cal = []
    week = []
    week_headers = []

    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        cal_day['event'] = False
        for event in event_list:
            if day >= event.start_date.date() and day <= event.end_date.date():
                cal_day['event'] = True
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False  
        week.append(cal_day)
        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += datetime.timedelta(1)

    return {'calendar': month_cal, 'headers': week_headers}

register.inclusion_tag('blog/tags/calendar.html')(month_cal)
