from django.db.models import Manager
from django.conf import settings
import datetime

class PublishedManager(Manager):
    """Returns published posts that are not in the future.""" 
    
    def published(self, **kwargs):
        return self.get_query_set().filter(status__gte=2, pub_date__lte=datetime.datetime.now(), sites__id__exact=settings.SITE_ID, **kwargs)

