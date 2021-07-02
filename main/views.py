from django.db.models import Q
import django_filters.rest_framework as filters
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Product, Review, Likes, Favorite, Cart
from .permissions import IsAuthororAdminPermission, DenyAll
from .serializers import (ProductListSerializer,
                          ProductDetailsSerializer, ReviewSerializer, FavoriteListSerializer, CartSerializer)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ['title', 'price']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['create_review', 'like', 'favorites']:
            return [IsAuthenticated()]
        return []

    # api/v1/products/products/id/like/
    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        product = self.get_object()
        user = request.user
        like_obj, created = Likes.objects.get_or_create(product=product, user=user)

        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')

    # api/v1/products/products/id/favorites/
    @action(detail=True, methods=['POST'])
    def favorites(self, request, pk):
        product = self.get_object()
        user = request.user
        fav, created = Favorite.objects.get_or_create(product=product, user=user)
        if fav.favorite:
            fav.favorite = False
            fav.save()
            return Response('removed from favorites')
        else:
            fav.favorite = True
            fav.save()
            return Response('added to favorites')

    @action(detail=False, methods=["GET"])
    def search(self, request, pk=None):
        q = request.query_params.get("q")  # request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))

        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthororAdminPermission()]


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAdminUser()]
        else:
            return [DenyAll()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class FavoriteView(ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}