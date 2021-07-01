from rest_framework import serializers
from .models import Product, Review, Favorite, Cart, CartItem
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'image')


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def get_rating(self, instance):
        total_rating = sum(instance.reviews.values_list('rating', flat=True))
        reviews_count = instance.reviews.count()
        rating = total_rating / reviews_count if reviews_count > 0 else 0
        return round(rating, 1)

    def get_likes(self, instance):
        total_likes = sum(instance.likes.values_list('is_liked', flat=True))
        likes = total_likes if total_likes > 0 else 0
        return likes

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation['rating'] = self.get_rating(instance)
        representation['likes'] = self.get_likes(instance)
        return representation


class ReviewAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full_name'] = 'Anonymous User'
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('id', 'author')

    def validate_product(self, product):
        request = self.context.get('request')
        if product.reviews.filter(author=request.user).exists():
            raise serializers.ValidationError('You cannot add second review to this product')
        return product

    def validate_rating(self, rating):
        if not rating in range(1, 6):
            raise serializers.ValidationError('Rating must be from 1 to 5')
        return rating

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = ReviewAuthorSerializer(instance.author).data
        return rep


class CartItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField(source='get_total_price')

    class Meta:
        model = CartItem
        fields = ('product', 'amount', 'price')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, write_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', )

    def create(self, validated_data):
        request = self.context.get('request')
        items = validated_data.pop('items')
        user = request.user
        cart = Cart.objects.create(user=user)
        for item in items:
            CartItem.objects.create(cart=cart, product=item['product'], amount=item['amount'])
        return cart

    def to_representation(self, instance):
        representation = super(CartSerializer, self).to_representation(instance)
        representation['user'] = instance.user.email
        representation['products'] = CartItemSerializer(instance.cartitem.all(), many=True).data
        return representation


class FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductDetailsSerializer(Product.objects.filter(favorites=instance.id),
                                                             many=True, context=self.context).data
        return representation

