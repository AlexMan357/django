from rest_framework import serializers
from .models import Product, Order


class ProductSerialize(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_by",
            "archived",
            "preview",
        )


class OrderSerialize(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "pk",
            "delivery_address",
            "promocode",
            "user",
            "products",
            "receipt",
        )