from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=70, unique=True)
    slug = models.SlugField(max_length=70, primary_key=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products', blank=True, null=True)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product/', blank=True, null=True)


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='reviews')
    text = models.TextField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['author', 'product']
        ordering = ('-created_at', )


class StatusChoices(models.TextChoices):
    new = ('new', 'New')
    in_progress = ('in_progress', 'In progress')
    done = ('done', 'Done')
    cancelled = ('cancelled', 'Cancelled')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                             related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItems')
    status = models.CharField(max_length=15, choices=StatusChoices.choices)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


class OrderItems(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.DO_NOTHING,
                              related_name='items')
    product = models.ForeignKey(Product,
                                on_delete=models.DO_NOTHING,
                                related_name='order_items')
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ['order', 'product']


class Likes(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='likes')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)

    is_liked = models.BooleanField(default=False)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    favorite = models.BooleanField(default=False)



