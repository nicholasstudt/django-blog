# Create your views here.
from django import http
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.db.models import Q
from django.views.generic import date_based, list_detail

from blog.models import Entry, Author, Tag

def entry_list(request, author=None, page=0, **kwargs):

    try:
        paginate_by = settings.BLOG_PAGINATE_ENTRY_LIST
    except AttributeError:
        paginate_by = 10

    if author:
        object = get_object_or_404(Author, ident=author)
        queryset = Entry.objects.published(author=object)
    else: 
        queryset = Entry.objects.published()

    return list_detail.object_list(
        request,
        page = page,
        paginate_by = paginate_by,
        queryset = queryset,
        **kwargs
    )
entry_list.__doc__ = list_detail.object_list.__doc__

def tag_list(request, ident, page=0, **kwargs):

    # Should this take more than one tag at a time?
    tag = get_object_or_404(Tag, tag=ident)

    try:
        paginate_by = settings.BLOG_PAGINATE_TAG_LIST
    except AttributeError:
        paginate_by = 10

    return list_detail.object_list(
        request,
        page = page,
        paginate_by = paginate_by,
        queryset = Entry.objects.published(tags__id__exact=tag.pk),
        template_name = 'blog/tag_list.html',
        extra_context = {'tag': tag },
        **kwargs
    )
tag_list.__doc__ = list_detail.object_list.__doc__

def entry_latest(request, **kwargs):
    
    if request.user.is_staff: # Restrict preview to staff
        queryset = Entry.objects.all_published()
        future = True
    else:
        queryset = Entry.objects.published()
        future = False

    latest = queryset[0]

    return date_based.object_detail(
        request,
        month_format = '%m',
        year = latest.pub_date.year,
        month = latest.pub_date.month,
        day = latest.pub_date.day,
        object_id = latest.id,
        date_field = 'pub_date',
        queryset = queryset,
        allow_future = future,
        template_name = 'blog/entry_latest.html',
        **kwargs
    )
entry_latest.__doc__ = date_based.object_detail.__doc__

def entry_detail(request, year, month, day, slug, **kwargs):
    
    if request.user.is_staff: # Restrict preview to staff
        queryset = Entry.objects.all_published()
        future = True
    else:
        queryset = Entry.objects.published()
        future = False

    # If we are an authenticated user with the ability to
    # add/edit/delete an entry then we need to use a different manager.
    return date_based.object_detail(
        request,
        month_format = '%m',
        year = year,
        month = month,
        day = day,
        slug = slug,
        date_field = 'pub_date',
        queryset = queryset,
        allow_future = future,
        **kwargs
    )
entry_detail.__doc__ = date_based.object_detail.__doc__

def entry_search(request, template_name='blog/entry_search.html'):
    response = {}
    # This should check tags, and headlines as well.
    if request.POST:
        search_term = '%s' % request.POST['q']
        post_list = Entry.objects.published().filter(
                                Q(content__icontains=search_term) |
                                #Q(tags__icontains=search_term) |
                                Q(headline__icontains=search_term) )
        response = {'object_list': post_list, 'search_term':search_term}
    return render_to_response(template_name,     
                                response,
                                context_instance=RequestContext(request))
        

def entry_archive_year(request, year, **kwargs):
    return date_based.archive_year(
        request,
        year = year,
        date_field = 'pub_date',
        queryset = Entry.objects.published(),
        make_object_list = True,
        **kwargs
    )
entry_archive_year.__doc__ = date_based.archive_year.__doc__

def entry_archive_month(request, year, month, **kwargs):
    return date_based.archive_month(
        request,
        year = year,
        month = month,
        date_field = 'pub_date',
        month_format = '%m',
        queryset = Entry.objects.published(),
        **kwargs
    )
entry_archive_month.__doc__ = date_based.archive_month.__doc__

def entry_archive_day(request, year, month, day, **kwargs):
    return date_based.archive_day(
        request,
        year = year,
        month = month,
        day = day,
        date_field = 'pub_date',
        month_format = '%m',
        queryset = Entry.objects.published(),
        **kwargs
    )
entry_archive_day.__doc__ = date_based.archive_day.__doc__

def author_detail(request, ident, **kwargs):
    return list_detail.object_detail(
            request,
            slug = ident,
            slug_field = 'ident',
            queryset = Author.objects.all(),
            **kwargs )
author_detail.__doc__ = list_detail.object_detail.__doc__

def author_list(request, page=0, **kwargs):

    try:
        paginate_by = settings.BLOG_PAGINATE_AUTHOR_LIST
    except AttributeError:
        paginate_by = 10

    return list_detail.object_list(
            request,
            page = page,
            paginate_by = paginate_by,
            queryset = Author.objects.all(),
            **kwargs )
