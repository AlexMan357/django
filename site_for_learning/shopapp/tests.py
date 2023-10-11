from django.contrib.auth.models import User, Permission
from django.http import HttpResponse
from django.test import TestCase

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers
from django.urls import reverse
from string import ascii_letters
from random import choices
from django.conf import settings


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(1, 2)
        self.assertEqual(result, 3)


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="qwerty")
        permission = Permission.objects.get(codename="add_product")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123",
                "description": "A good table",
                "discount": "10",
                "created_by": self.user.pk
            },
            HTTP_USER_AGENT='Mozilla/5.0',
        )

        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="qwerty")
        cls.product = Product.objects.create(name="Best Product", created_by_id=cls.user.pk)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.user.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse(
                "shopapp:product_details",
                kwargs={"pk": self.product.pk},
            ),
            HTTP_USER_AGENT='Mozilla/5.0',

        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse(
                "shopapp:product_details",
                kwargs={"pk": self.product.pk},
            ),
                HTTP_USER_AGENT='Mozilla/5.0',
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "product-fixtures.json",
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"), HTTP_USER_AGENT='Mozilla/5.0')
        # for product in Product.objects.filter(archived=False).all():
        #     self.assertContains(response.product.name)

        # products = Product.objects.filter(archived=False).all()
        # products_ = response.context["products"]
        # for p, p_ in zip(products, products_):
        #     self.assertEqual(p.pk, p_.pk)

        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )

        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.credentials = dict(username="test", password="qwerty")
        cls.user = User.objects.create_user(username="test", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertContains(response, "Orders")

    def test_orders_view_not_authentificated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"), HTTP_USER_AGENT='Mozilla/5.0')
        # self.assertRedirects(response, str(settings.LOGIN_URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "product-fixtures.json",
    ]
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:product_export"),
            HTTP_USER_AGENT='Mozilla/5.0',
        )

        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]

        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="test", password="qwerty")
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)
        cls.order = Order.objects.create(
            delivery_address="Street",
            promocode="AAA",
            user=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        cls.order.delete()
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_order_details(self):
        response = self.client.get(
            reverse(
                "shopapp:order_details",
                kwargs={"pk": self.order.pk},
            ),
            HTTP_USER_AGENT='Mozilla/5.0',

        )
        self.assertEqual(response.status_code, 200)

    def test_get_order_and_check_content(self):
        response = self.client.get(
            reverse(
                "shopapp:order_details",
                kwargs={"pk": self.order.pk},
            ),
            HTTP_USER_AGENT='Mozilla/5.0',
        )
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        # print(response.context['order'].pk)
        self.assertEqual(self.order.pk, response.context['order'].pk)


class OrdersExportViewTestCase(TestCase):
    fixtures = [
        "user-fixtures.json",
        "product-fixtures.json",
        "order-fixtures.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test", password="qwerty", is_staff=1)
        print("USER", cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(
            reverse("shopapp:order_export"),
            HTTP_USER_AGENT='Mozilla/5.0',
        )

        self.assertEqual(response.status_code, 200)
        orders = Order.objects.prefetch_related("products").all()


        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]

        orders_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            orders_data["orders"],
            expected_data,
        )
