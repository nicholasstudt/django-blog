from django.conf.urls.defaults import *

urlpatterns = patterns('blog.views',

    # /article/<section>/<date "YYYY-MM-DD">/<ident> -> One article

    # /archive/<section>/<date-part "YYYY-MM-DD">

    # /author/<author ident>

    # /search
    (r'^search/$', 'search'),

    # / -> frontpage
    (r'^$', 'post_list'),
)
