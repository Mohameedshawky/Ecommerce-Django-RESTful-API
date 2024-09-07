from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.TextChoices):
    COMPUTERS = 'Computer', 'Computers'
    LAPTOP = 'Laptop', 'Laptops'
    GAMES = 'Games', 'Games'
    PHONES = 'Phones', 'Phones'
    FOOD = 'Food', 'Food'
    CLOTHES = 'Clothes', 'Clothes'
    ELECTRONICS = 'Electronics', 'Electronics'
    FURNITURE = 'Furniture', 'Furniture'
    BEAUTY = 'Beauty', 'Beauty & Personal Care'
    BOOKS = 'Books', 'Books'
    TOYS = 'Toys', 'Toys & Games'
    JEWELRY = 'Jewelry', 'Jewelry'
    SPORTS = 'Sports', 'Sports & Outdoors'
    HEALTH = 'Health', 'Health & Wellness'
    AUTOMOTIVE = 'Automotive', 'Automotive'
    PETS = 'Pets', 'Pet Supplies'
    HOME_APPLIANCES = 'Home Appliances', 'Home Appliances'
    OFFICE_SUPPLIES = 'Office Supplies', 'Office Supplies'
    BABY_PRODUCTS = 'Baby Products', 'Baby Products'
    MUSIC = 'Music', 'Music & Instruments'



class Product(models.Model):
    name = models.CharField(max_length=100,default="",blank=False)
    description = models.TextField(max_length=500,default="",blank=False)
    price = models.DecimalField(max_digits=7,decimal_places=2,default=0)
    brand = models.CharField(max_length=100,default="",blank=False)
    category = models.CharField(max_length=100,choices=Category.choices)
    ratings = models.DecimalField(max_digits=3,decimal_places=2,default=0)
    stock = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)    

    def __str__(self):
        return self.name + ', ' + self.category


class Review(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE,related_name='reviews')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000,default="",blank=False) 
    createAt = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.comment