from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin, ImportCsvMixin
from django.urls import path


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


class OrderInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin, ImportCsvMixin):
    change_list_template = 'shopapp/product_changelist.html'
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]

    # list_display = "pk", "name", "description", "price", "discount"
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),
         }),
        ("Price Options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse",)
        }),
        ("Images", {
            "fields": ("preview",),
        }),
        ("Extra Options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        }),

    ]
    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 50:
            return obj.description
        return obj.description[:50] + '...'

    # def import_csv(self, request: HttpRequest) -> HttpResponse:
    #     if request.method == "GET":
    #         form = CSVImportForm()
    #         context = {
    #             "form": form
    #         }
    #         return render(request, "admin/csv_form.html", context)
    #     form = CSVImportForm(request.POST, request.FILES)
    #     if not form.is_valid():
    #         context = {
    #             "form": form,
    #         }
    #         return render(request, "admin/csv_form.html", context, status=400)
    #     save_csv_products(
    #         file=form.files["csv_file"].file,
    #         encoding=request.encoding,
    #     )
    #
    #     self.message_user(request, "Data from CSV was imported")
    #     return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",

            )
        ]
        return new_urls + urls


# admin.site.register(Product, ProductAdmin)
# class ProductInline(admin.TabularInline):


class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ImportCsvMixin):
    change_list_template = 'shopapp/order_changelist.html'
    inlines = [
        ProductInline,
    ]

    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",

            )
        ]
        return new_urls + urls
