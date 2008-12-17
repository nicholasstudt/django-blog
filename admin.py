
from django.contrib import admin
from blog.models import Author
from blog.models import Entry

#class AuthorAdmin(admin.ModelAdmin):
#    list_display = ('name')


admin.site.register(Author)
admin.site.register(Entry)
