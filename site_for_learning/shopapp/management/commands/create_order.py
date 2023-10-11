from typing import Sequence

from django.core.management import BaseCommand
from shopapp.models import Order, Product
from django.contrib.auth.models import User
from django.db import transaction

class Command(BaseCommand):
    """
    Create orders
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username='admin')
        # products: Sequence[Product] = Product.objects.defer("description", "price", "created_at").all()
        products: Sequence[Product] = Product.objects.only("id").all()
        order, created = Order.objects.get_or_create(
            delivery_address='ul Gogolya,d 12',
            promocode='promo10',
            user=user
        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(self.style.SUCCESS("Order created"))