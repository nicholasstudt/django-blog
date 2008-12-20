# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader

from blog.models import Entry, Author, Tag

def post_list(request):
    return render_to_response('blog/list.html', {
            'error_message': "You didn't select a choice.",
        })


