from django.contrib.auth.models import User, Group
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import yaml

from backend.models import Product, Shop, Category, Parameter, ProductParameter
from backend.serializers import ProductSerializer, UserSerializer, GroupSerializer


class ProductView(APIView):
    def get(self, request, *args, **kwargs):
        shop = Shop.objects.create(name='Svyaznoi', state=True)
        Product.objects.create(name='iPhone', category='phones', quantity=20,
                               price=80000, shop=shop)
        queryset = Product.objects.all().select_related('shop')
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data)
        else:
            return Response(serializer.errors)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


def import_data(request):
    if request.method == 'POST':
        yaml_file = request.FILES['yaml_file']

        data = yaml.load(yaml_file, Loader=yaml.FullLoader)

        shop_name = data.get('shop')
        categories = data.get('categories')
        goods = data.get('goods')

        shop = Shop.objects.create(name=shop_name)

        for category_data in categories:
            category = Category.objects.create(name=category_data['name'])

        for good_data in goods:
            category_id = good_data['category']
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                category=category,
                model=good_data['model'],
                name=good_data['name'],
                price=good_data['price'],
                price_rrc=good_data['price_rrc'],
                quantity=good_data['quantity']
            )

            parameters_data = good_data.get('parameters', {})
            for parameter_name, parameter_value in parameters_data.items():
                parameter, created = Parameter.objects.get_or_create(name=parameter_name)
                ProductParameter.objects.create(product=product, parameter=parameter, value=parameter_value)

        return render(request, 'import_success.html')

    return render(request, 'import_form.html')
