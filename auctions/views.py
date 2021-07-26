from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import reverse_related
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from auctions.models import User, Listing, Bid, Comment, Watchlist


def index(request):
    # buyer=None gets only the objects that have not been bought, i.e. the 'active' listings
    listings = Listing.objects.filter(buyer=None)
    context = {
        "listings": listings,
    }
    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="/login/")
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")

    elif request.method == "POST":
        valid_categories = ["", "books", "electronics", "home_kitchen", "toys"]
        
        form_name = request.POST["name"]
        form_price = request.POST["price"]
        form_description = request.POST["description"]
        form_image = request.POST["image"]
        form_category = request.POST["category"]

    if form_category not in valid_categories:
        return render(request, "auctions/error.html", {"message": "Invalid category"})

    #save object to model
    obj = Listing.objects.create(
        name=form_name, 
        initial_price=form_price, 
        description=form_description, 
        image=form_image, 
        category=form_category,
        seller=request.user
        )
    #retrieve newly saved object from model to pass arguments to listing_view()
    id = obj.pk
        
    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))


def listing_view(request, id):
    try:
        listing_item = Listing.objects.filter(pk=id)[0]
    except:
        return render(request, "auctions/error.html", {"message": "Page does not exist"})
    comments = Comment.objects.filter(listing=id)  
    try:
        watchlist_item = Watchlist.objects.get(listing=id, user=request.user)
    except:
        watchlist_item = None
    bids = Bid.objects.filter(listing=id)  
    bid_list = [bid.bid_amount for bid in bids]
    try:
        highest_bid = max(bid_list)
    except:
        highest_bid = None

    if len(bids) == 0:
        min_price = float(listing_item.initial_price) + 0.01
    else:
        min_price = float(highest_bid) + 0.01

    context = {
        "listing": listing_item,
        "comments": comments,
        "watchlist": watchlist_item,
        "bid": highest_bid,
        "min_price": min_price,
        "current_user": request.user.id
    }
    return render(request, "auctions/listing.html", context)


@login_required(login_url="/login/")
def display_watchlist(request):
    watchlistings = Watchlist.objects.filter(user=request.user)  # gets Watchlist objects owned by the current user
    watch_ids = [watchlisting.listing.id for watchlisting in watchlistings]  # gets Listing ID for each of the above
    listings = [Listing.objects.filter(id=watch_id).first() for watch_id in watch_ids]  # 

    context = {
        "listings": listings,
    }
    return render(request, "auctions/watchlist.html", context)


@login_required(login_url="/login/")
def add_to_watchlist(request, id):
    if request.method == "POST":
        listing_item = Listing.objects.get(pk=id)
        user_id = request.user
        obj = Watchlist.objects.create(
            listing=listing_item,
            user=user_id
        )
    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))


@login_required(login_url="/login/")
def remove_from_watchlist(request, id):
    if request.method == "POST":
        obj = Watchlist.objects.filter(listing=id, user=request.user)
        obj[0].delete()
    
    return HttpResponseRedirect(reverse("auctions:watchlist"))


@login_required(login_url="/login/")
def bid(request, id):
    # do internal error checking for bid amount; must be greater than existing highest bid
    if request.method == "POST":
        listing_item = Listing.objects.get(pk=id)
        user_bid = request.POST["bid"]

        bids = Bid.objects.filter(listing=id)  
        bid_list = [bid.bid_amount for bid in bids]
        
        if len(bid_list) == 0:
            min_bid = float(listing_item.initial_price) + 0.01
        else:
            highest_bid = max(bid_list)
            min_bid = float(highest_bid) + 0.01
        
        if float(user_bid) < min_bid:
            return render(request, "auctions/error.html", {"message": "Insufficient Bid Amount"})

        obj = Bid.objects.create(
            listing=listing_item,
            bid_amount=user_bid,
            user=request.user
        )

    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))


@login_required(login_url="/login/")
def add_comment(request, id):
    if request.method == "POST":
        comment = request.POST["comment"]
        if not comment:
            return render(request, "auctions/error.html", {"message": "Comment is insufficient length"})
        listing_item = Listing.objects.get(pk=id)
        c = Comment.objects.create(
            listing=listing_item, 
            content=comment,
            user=request.user
        )

    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))


@login_required(login_url="/login/")
def end_auction(request, id):
    if request.method == "POST":
        # get highest bid for that listing
        bids = Bid.objects.filter(listing=id)  
        bid_list = [bid.bid_amount for bid in bids]
        highest_bid = max(bid_list)
        # get user who made that bid
        high_bid_obj = Bid.objects.get(bid_amount=highest_bid)
        high_bid_user = high_bid_obj.user.id
        # set Listing's buyer value to the user id who made the winning bid
        listing_item = Listing.objects.get(id=high_bid_user)
        # get the User object of the highest bid
        highest_bidder = User.objects.get(pk=high_bid_user)
        listing_item.buyer = highest_bidder
        listing_item.sale_price = highest_bid
        listing_item.save()
        
    return HttpResponseRedirect(reverse("auctions:index"))


def categories(request):
    """display categories of listings, click each one to be shown listings that match"""
    if request.method == "POST":
        cat = request.POST["category"]
        listings = Listing.objects.filter(category=cat, buyer=None)
        context = {
            "listings": listings,
        }
        return render(request, "auctions/index.html", context)
    else:
        return render(request, "auctions/categories.html")


@login_required(login_url="/login/")
def display_sales(request):
    """display listings the user has sold, and for how much, and when"""
    sales_items = Listing.objects.filter(seller=request.user).exclude(buyer=None)
    context = {
        "listings": sales_items
    }
    return render(request, "auctions/sales.html", context)


@login_required(login_url="/login/")
def display_purchases(request):
    """display listings the user has purchased, and for how much, and when"""
    purchases = Listing.objects.filter(buyer=request.user)
    context = {
        "listings": purchases
    }
    return render(request, "auctions/purchases.html", context)

