from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    def items(self):                # items() method returns the QuerySet of objects to include in this sitemap
        return Post.published.all()
    def lastmod(self, obj):         # lastmod method receives each object returned by items() and returns the last time the object was modified. 
        return obj.updated

