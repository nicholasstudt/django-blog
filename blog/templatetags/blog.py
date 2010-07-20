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
    def __init__(self, year, month, author=None):
        self.year = year 
        self.month = month 
        self.author = author 

    def render(self, context):
        year = self.year
        month = self.month
        author = self.author

        if self.author:
            try: 
                author = Author.objects.get(ident=self.author)
            except ObjectDoesNotExist: 
                pass
           
        if author:
            event_list = Entry.objects.published_bymonth(year, month, author=author)
        else: 
            event_list = Entry.objects.published_bymonth(year, month)

        # Fix this to just use calendar.* for all math.

        start = datetime.date(year, month, 1)
        end = datetime.date(year, month, calendar.monthrange(year, month)[1])

        first_day_of_calendar = start - datetime.timedelta(start.weekday()) 
        last_day_of_calendar = end + datetime.timedelta(7 - end.weekday())

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
                if day >= event.pub_date.date() and day <= event.pub_date.date():
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
    
        t = template.loader.get_template('blog/tags/calendar.html')

        return t.render(template.Context({'month': start, 'calendar': month_cal, 'headers': week_headers}, autoescape=context.autoescape))

class TagList(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = Tag.objects.all()
        return ''

@register.tag
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

@register.tag
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

@register.tag
def month_calendar(parser, token):
    """
    Create a calendar of a month with the days that have entries linked
    to that day in the archive.

    If provided a negative difference it will render the month in the
    past. -1 will render last month, -2 will render two months ago, etc. 

    Example::

        {% month_calendar <year> <month> [author_ident] %}
        {% month_calendar <difference> [author_ident] %}
        
        {% load blog %}

        {% month_calendar 2010 11 author_ident_here %} 
        {% month_calendar 2010 11 %} 
        
        {% month_calendar -1 author_ident_here %} 
        {% month_calendar -1 %} 

    """
   
    author = difference = None
    year = datetime.date.today().year
    month = datetime.date.today().month

    bits = token.contents.split()

    # AUTHOR -OR- DIFFERENCE
    if len(bits) == 2:
        try:
            difference = int(bits[1])
        except ValueError:
            author = bits[1]

    # YYYY MM  -OR- DIFFERENCE AUTHOR
    if len(bits) == 3:
        try: 
            year = int(bits[1])
            month = int(bits[2])
        except ValueError:
            difference = bits[1]
            author = bits[2]
           

    # YYYY MM AUTHOR
    if len(bits) == 4:
        year = bits[1]
        month = bits[2]
        author = bits[3]

    if difference:
        today = datetime.date.today()
        year = today.year
        month = today.month

        if difference > 0:
            month += difference
            while month > 12:
                month -= 12
                year += 1
        else:
            month += difference
            while month < 0:
                month += 12
                year -= 1

    try: 
        year = int(year)
    except ValueError: 
        year = datetime.date.today().year
    
    try: 
        month = int(month)
    except ValueError: 
        month = datetime.date.today().month

    return Calendar(year, month, author)
