import django_filters

from .models import Product

class ProductsFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category", lookup_expr="icontains")
    keyword = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="icontains")
    minPrice = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    maxPrice = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ('category', 'brand','keyword','minPrice','maxPrice')