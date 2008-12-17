from django.contrib import admin

from blog.models import Author
from blog.models import Entry
from blog.models import Tag

# Can't put manytomany inline ?
class TagInline(admin.TabularInline):
    model = Tag

class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,      {'fields':['headline','author','pub_date']}),
        ('Advanced',    {'fields':['slug'], 'classes': ['collapse'] }),
        ('Content',     {'fields':['content','tags']}),
    ]
#    inlines = [TagInline]
    prepopulated_fields = {'slug': ('headline',)}
    list_display = ('headline','author','pub_date',)
    list_filter = ('pub_date',)
    search_fields = ['headline']
    date_hierarchy = 'pub_date'



admin.site.register(Entry, EntryAdmin)
admin.site.register(Author)
admin.site.register(Tag)
