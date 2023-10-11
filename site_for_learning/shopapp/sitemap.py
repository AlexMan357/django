from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from shopapp.models import Product


class ShopSiteMap(Sitemap):
    changefreq = "always"
    priority = 0.9

    def items(self):
        return (Product.objects
                .filter(archived=False)
                .order_by("-create_at")
                )
