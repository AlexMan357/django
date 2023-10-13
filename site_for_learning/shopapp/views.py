"""
В этом модуле лежат различные наборы представлений.

Разные view для интернет-магазина: по товарам, заказам и т.д.
"""
import logging
from django.core import serializers
from django.contrib.syndication.views import Feed


from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from timeit import default_timer
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

# from site_for_learning.settings import LOGIN_URL
from .common import common_read_csv_file
from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order
from django.views import View
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from drf_spectacular.utils import(
    extend_schema,
    OpenApiResponse,
)
from .serializer import ProductSerialize, OrderSerialize

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

from django_filters.rest_framework import DjangoFilterBackend
from csv import DictWriter
from django.utils.decorators import method_decorator
from django.core.cache import cache

log = logging.getLogger(__name__)


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Product.objects
            .filter(archived=False)
            .order_by("-create_at")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:10]


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара.
    """
    model = Product
    queryset = Product.objects.all()
    serializer_class = ProductSerialize
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]

    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary='Get one product by id',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerialize,
            404: OpenApiResponse(description='Empty response, product by id not found'),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60*2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = "products-export.csv"
        response["Content-Desposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        methods=['post'],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request):
        products = common_read_csv_file(
            file=request.FILES["file"].file,
            encoding=request.encoding,
            model=self.model
        )
        self.model.save_csv(products)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    """
    Набор представлений для действий над Order.

    Полный CRUD для сущностей заказа.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerialize
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "delivery_address",
        "promocode",
        "products",
    ]

    ordering_fields = [
        "user",
        "delivery_address",
    ]


class ShopIndexView(View):
    """Представление для shop."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Метод  обрабатывает get-запрос для страницы shop-index.html."""
        countries = {
            ('Russia', 143),
            ('Belarus', 9),
            ('India', 1423),
        }
        context = {
            'time_running': default_timer(),
            'countries': countries,
            'items': 5,
        }
        log.debug("Countries for shop index: %s", countries)
        log.info("Rendering shop index")
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    """Представление для групп."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Метод  обрабатывает get-запрос для страницы groups-list.html."""
        form = GroupForm()
        context = {
            "groups": Group.objects.prefetch_related('permissions').all(),
            "form": form,
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        """Метод  обрабатывает post-запрос для страницы groups-list.html."""
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


# class ProductDetailsView(View):
#     def get(self, request: HttpRequest, pk: int) -> HttpResponse:
#         product = get_object_or_404(Product, pk=pk)
#         context = {
#             "product": product,
#         }
#         return render(
#           request,
#           'shopapp/product-details.html',
#           context=context
#           )


class ProductDetailsView(DetailView):
    """Представление для деталей товаров."""

    template_name = 'shopapp/product-details.html'
    model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


# class ProductsListView(TemplateView):
#     template_name = 'shopapp/products-list.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["products"] = Product.objects.all()
#         return context


class ProductsListView(ListView):
    """Представление для набора товаров."""

    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


# def products_list(request: HttpRequest) -> HttpResponse:
#     """Ф-я view для вывода всех продуктов """
#     context = {
#         "products": Product.objects.all()
#     }
#     return render(request, 'shopapp/products-list.html', context=context)


# def create_product(request: HttpRequest) -> HttpResponse:
#     """ Ф-я view для создания продукта на странице """
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # name = form.cleaned_data["name"]
#             # price = form.cleaned_data["price"]
#             # Product.objects.create(**form.cleaned_data)
#
#             form.save()
#             url = reverse("shopapp:products_list")
#             return redirect(url)
#     else:
#         form = ProductForm()
#     context = {
#         "form": form,
#     }
#     return render(request, 'shopapp/create-product.html', context=context)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    """
    Представление для создания нового товара.

    Создание новой сущности товара - для пользователей с данными правами.
    """

    # template_name = 'shopapp/product-details.html'
    permission_required = "shopapp.add_product"
    model = Product
    # fields = "name", "price", "description", "discount"
    form_class = ProductForm
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        super().form_valid(form)
        return HttpResponseRedirect(reverse_lazy('shopapp:products_list'))


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            Product.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def test_func(self):
        no_superuser_get_access = False
        is_true_permission = False

        product_author = self.get_object().created_by # Product.objects.select_related("created_by").get(pk=self.get_object().id)
        if product_author == self.request.user:
            no_superuser_get_access = True

        user_permission = self.request.user.get_user_permissions()
        if "shopapp.change_product" in user_permission:
            is_true_permission = True

        return any([self.request.user.is_superuser, no_superuser_get_access, is_true_permission])

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)

# def orders_list(request: HttpRequest) -> HttpResponse:
#     """ Ф-я view для вывода всех заказов """
#     context = {
#         "orders": Order.objects.select_related("user").prefetch_related("products").all()
#     }
#     return render(request, 'shopapp/order-list.html', context=context)


# def create_order(request: HttpRequest) -> HttpResponse:
#     """ Ф-я view для создания заказа на странице """
#     if request.method == "POST":
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             form.save()
#             url = reverse("shopapp:orders_list")
#             return redirect(url)
#     else:
#         form = OrderForm()
#
#     context = {
#         "form": form,
#     }
#     return render(request, 'shopapp/create-order.html', context=context)

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('shopapp:orders_list')


class UserOrdersListView(ListView):
    """ Реализует страницу со списком заказов пользователя """

    template_name = 'shopapp/user_order_list.html'
    context_object_name = "user_orders_list"
    owner = None

    def get_queryset(self):
        print("UserOrdersListView.get_queryset")
        user_id = self.kwargs['user_id']
        get_object_or_404(User, pk=user_id)
        queryset = Order.objects.filter(user=user_id).prefetch_related('products').all()
        self.owner = queryset
        return queryset

    def get_context_data(self, **kwargs):
        print("UserOrdersListView.get_context_data")
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.owner
        return context

    def get(self, *args, **kwargs):
        print('UserOrdersListView.Processing GET request')
        response = super().get(*args, **kwargs)
        # print(args)
        # print(kwargs)
        print('UserOrdersListView.Finished processing GET request')
        if args[0].user.is_authenticated:
            return response
        return redirect(reverse("myauth:login")) #LOGIN_URL


class OrdersListView(LoginRequiredMixin, ListView):
    """ Реализует страницу со списком заказов всех пользователей """
    template_name = 'shopapp/order_list.html'
    queryset = {
        user:
        Order.objects
        .filter(user=user.pk)
        .prefetch_related('products')
        .all()
        for user in User.objects.only("pk", "username").all()

    }


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order",
    queryset = (
                 Order.objects
                 .select_related("user")
                 .prefetch_related("products")
                 )


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        product_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]

        elem = product_data[0]
        name = elem["name"]
        print("name:", name)
        return JsonResponse({"products": product_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        product_cache = cache.get(cache_key)
        if product_cache is None:
            orders = Order.objects.prefetch_related("products").all()
            order_data = [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promocode": order.promocode,
                    "user": order.user.pk,
                    "products": [product.pk for product in order.products.all()],
                }
                for order in orders
            ]
            cache.set(cache_key, order_data, 300)
            
        return JsonResponse({"orders": order_data})

    def test_func(self):
        return self.request.user.is_staff


class UserOrdersExportView(View):
    """ представление для экспорта данных о заказах выбранного пользователя """
    def get(self, *args, **kwargs):
        user_id = kwargs['user_id']
        get_object_or_404(User, pk=user_id)

        cache_key = f'orders_data_export_user_id_{user_id}'
        data = cache.get(cache_key)
        print("DATA", data)

        if data is None:
            print("DATA from database")
            queryset = Order.objects.filter(user=user_id).prefetch_related('products').order_by('pk').all()
            data = OrderSerialize(queryset, many=True)
            cache.set(cache_key, data, 60*3)

        return JsonResponse(data.data, safe=False)

