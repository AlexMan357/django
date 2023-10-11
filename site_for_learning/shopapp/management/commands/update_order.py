from django.core.management import BaseCommand
from shopapp.models import Order, Product
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Update orders
    """
    def handle(self, *args, **options):
        self.stdout.write("Update order")
        order = Order.objects.first()
        if not order:
            self.stdout.write("no order found")
            return

        products = Product.objects.all()

        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(self.style.SUCCESS(f"aded products {order.products.all} to order {order}"))