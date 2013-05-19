# Create your views here.
from django import http
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.db.models import Q
#from django.views.generic import date_based, list_detail
#from django.views.generic.dates DateDetail
from django.views.generic.list import ListView
from django.views.generic import dates
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from blog.models import Entry, Author, Tag

class EntryList(ListView):

    try:
        paginate_by = settings.BLOG_PAGINATE_ENTRY_LIST
    except AttributeError:
        paginate_by = 10

    def get_queryset(self):
        author = self.kwargs.get('author', None)
        if author:
            object = get_object_or_404(Author, ident=author)
            queryset = Entry.objects.published(author=object)
        else:
            queryset = Entry.objects.published()
            
        return queryset

class TagList(ListView):

    template_name = 'blog/tag_list.html'
    extra_context = { }

    try:
        paginate_by = settings.BLOG_PAGINATE_TAG_LIST
    except AttributeError:
        paginate_by = 10

    def get_queryset(self):
        tag = get_object_or_404(Tag, tag=self.kwargs['ident'])
        self.extra_context.update( { 'tag': tag } )
        return Entry.objects.published(tags__id__exact=tag.pk)

    def get_context_data(self, **kwargs):
        context = super(TagList, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

class EntryLatest(dates.DateDetailView):
    template_name = 'blog/entry_latest.html',
    month_format = '%m'
    date_field = 'pub_date'
    latest = None

    def get_year(self):
        return self.latest.pub_date.year

    def get_month(self):
        return self.latest.pub_date.month

    def get_day(self):
        return self.latest.pub_date.day

    def get_object(self):
        if self.request.user.is_staff: # Restrict preview to staff
            queryset = Entry.objects.all_published()
            self.allow_future = True
        else:
            queryset = Entry.objects.published()
            self.allow_future = False
        self.latest = queryset[0]
        return self.latest

class EntryDetail(dates.DateDetailView):

    month_format = '%m'
    date_field = 'pub_date'

    def get_queryset(self):
        if self.request.user.is_staff: # Restrict preview to staff
            queryset = Entry.objects.all_published()
            self.future = True
        else:
            queryset = Entry.objects.published()
            self.future = False
        return queryset

class EntrySearch(TemplateView):
    template_name = 'blog/entry_search.html'

    def post(self, request):
        search_term = '%s' % request.POST['q']
        post_list = Entry.objects.published().filter(
            Q(content__icontains=search_term) |
            #Q(tags__icontains=search_term) |
            Q(headline__icontains=search_term) )
        response = {'object_list': post_list, 'search_term':search_term }
        return render_to_response(self.template_name, response)

class EntryArchiveYear(dates.YearArchiveView):
    date_field = 'pub_date'
    make_object_list = True

    def get_queryset(self):
        return Entry.objects.published()

class EntryArchiveMonth(dates.MonthArchiveView):
    date_field = 'pub_date'
    month_format = '%m'

    def get_queryset(self):
        return Entry.objects.published()

class EntryArchiveDay(dates.DayArchiveView):
    date_field = 'pub_date'
    month_format = '%m'

    def get_queryset(self):
        return Entry.objects.published()

class AuthorDetail(DetailView):
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    model = Author

class AuthorList(ListView):
    slug_field = 'ident'
    slug_url_kwarg = 'ident'
    model = Author
    try:
        paginate_by = settings.BLOG_PAGINATE_AUTHOR_LIST
    except AttributeError:
        paginate_by = 10

