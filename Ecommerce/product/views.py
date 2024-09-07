from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Product, Review
from .serializer import productSerializer
from .filters import ProductsFilter

from django.db.models import Avg

# Create your views here.
@api_view(['GET'])
def listing_Products(request):
    # products = Product.objects.all()
    # serializedProducts = productSerializer(products,many=True)
    filterset = ProductsFilter(request.GET,queryset=Product.objects.all().order_by('id'))
    count = filterset.qs.count()
    respage = 5
    paginator = PageNumberPagination()
    paginator.page_size = respage
    queryset = paginator.paginate_queryset(filterset.qs,request)
    
    serializedProducts = productSerializer(queryset,many=True)
    return Response({
        'Products':serializedProducts.data,
        'Per Page':respage,
        'Product Count':count
        }
        )

# @api_view(['GET'])
# def get_product_by_id(request,pk):
#     try:
#         product = Product.objects.get(id=pk)
#         serializedProduct = productSerializer(product)
#         return Response({'Products': serializedProduct.data},
#                           status=status.HTTP_200_OK)
#     except ObjectDoesNotExist:
#         return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
# OR ^^
@api_view(['GET'])
def get_product_by_id(request,pk):
    product = get_object_or_404(Product, id=pk )
    serializedProduct = productSerializer(product)
    return Response({'Products': serializedProduct.data},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def adding_new_product(request):
    if request.method == 'POST':
        deserializedData = productSerializer(data = request.data)
        if deserializedData.is_valid():
            Product.objects.create(**request.data,user=request.user)   # deserializedData.save()
            return Response({
                "status": "success",
                "data": deserializedData.data,
                "message": "Product added successfully."
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "data": deserializedData.errors,
            "message": "There was an error creating the product."
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request,pk):
    product = get_object_or_404(Product,id=pk)

    if product.user != request.user:
        return Response({'Error':'You cannot update this product!'},
                        status=status.HTTP_403_FORBIDDEN)
    product.name = request.data['name']
    product.description = request.data['description']
    product.price = request.data['price']
    product.brand = request.data['brand']
    product.category = request.data['category']
    product.ratings = request.data['ratings']
    product.stock = request.data['stock']

    product.save()
    serializer = productSerializer(product,many=False)
    return Response({"status":"Product is updated successfully.",
                    "Updated product":serializer.data},
                    status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request,pk):
    product = get_object_or_404(Product,id=pk)

    if product.user != request.user:
        return Response({'status':'You cannot delete this product!'},
                        status=status.HTTP_403_FORBIDDEN)
    
    product.delete()
    return Response({"status":"Product is deleted successfully."},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request,pk):
    user = request.user
    product = get_object_or_404(Product,id=pk)
    data = request.data
    review = product.reviews.filter(user=user)
   
    if data['rating'] <= 0 or data['rating'] > 5:
        return Response({"error":'Please select between 1 to 5 only'}
                        ,status=status.HTTP_400_BAD_REQUEST) 
    elif review.exists():
        new_review = {'rating':data['rating'], 'comment':data['comment'] }
        review.update(**new_review)

        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()

        return Response({'details':'Product review updated'})
    else:
        Review.objects.create(
            user=user,
            product=product,
            rating= data['rating'],
            comment= data['comment']
        )
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()
        return Response({'details':'Product review created'})
    


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request,pk):
    user = request.user
    product = get_object_or_404(Product,id=pk)
   
    review = product.reviews.filter(user=user)
   
 
    if review.exists():
        review.delete()
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0
            product.ratings = rating['avg_ratings']
            product.save()
            return Response({'details':'Product review deleted'})
    else:
        return Response({'error':'Review not found'},status=status.HTTP_404_NOT_FOUND)

