from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username


class Listing(models.Model):
    name = models.CharField(max_length=60)
    initial_price = models.DecimalField(max_digits=100, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=100, decimal_places=2, blank=True, null=True)
    description = models.CharField(max_length=120, blank=True, null=True)
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    category = models.CharField(max_length=30, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_sold = models.DateField(auto_now=True, blank=True, null=True)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="seller_listings")
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="purchases")

    def __str__(self):
        return self.name

""" 
if I have a listing, and I want to know all the bids that listing has, I can access 
"bids", which gets me all of the bids for that listing;
if Listing = television, then Listing.bids will get me all Bid objects where listing = television

Likewise, if I have a user, and I want to know all the bids that user has made, I can access "user_bids", which 
gets me all of the bids for that user;
if User = Harry, then User.user_bids will get me all the Bid objects where user = Harry
"""

class Bid(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_bids")
    bid_amount = models.DecimalField(max_digits=100, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.listing


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments")
    content = CharField(max_length=120)
    comment_date = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.listing


class Watchlist(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watchlist_items")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_watchlists")
    add_date = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.listing
