from django.contrib import admin

from blog.models import Author
from blog.models import Entry
from blog.models import Tag

class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['name','email']}),
        ('Advanced', {'fields':['ident'], 'classes': ['collapse'] }),
        ('Content', {'fields':['content']}),
    ]
    list_display = ('name','email')
    prepopulated_fields = {'ident': ('name',)}

class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['headline','author','status','pub_date']}),
        ('Advanced', {'fields':['sites','slug','comments'], 'classes': ['collapse'] }),
        ('Content', {'fields':['abstract','content','tags']}),
    ]
    prepopulated_fields = {'slug': ('headline',)}
    list_display = ('headline','author','pub_date',)
    list_filter = ('sites','status','pub_date',)
    search_fields = ['headline']
    date_hierarchy = 'pub_date'

admin.site.register(Entry, EntryAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Tag)
