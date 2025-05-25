from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Category
from .forms import CreateListingForm, BidForm, CommentForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect("index")
    return render(request, "auctions/create_listing.html", {
        "form": CreateListingForm()
    })


def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    is_owner = request.user == listing.owner
    is_winner = request.user == listing.winner
    in_watchlist = listing in request.user.watchlist.all() if request.user.is_authenticated else False

    if request.method == "POST":
        # Handle bid or comment
        if "place_bid" in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                new_bid = bid_form.cleaned_data["amount"]
                current_bid = listing.bids.last().amount if listing.bids.exists() else listing.starting_bid
                if new_bid > current_bid:
                    Bid.objects.create(listing=listing, bidder=request.user, amount=new_bid)
                    messages.success(request, "Your bid was placed successfully.")
                else:
                    messages.error(request, f"Your bid must be greater than the current bid (${current_bid}).")
        elif "add_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                Comment.objects.create(listing=listing, commenter=request.user, content=comment_form.cleaned_data["content"])
        elif "close_auction" in request.POST and is_owner:
            listing.active = False
            highest_bid = listing.bids.order_by("-amount").first()
            if highest_bid:
                listing.winner = highest_bid.bidder
            listing.save()
        elif "toggle_watchlist" in request.POST:
            if in_watchlist:
                request.user.watchlist.remove(listing)
            else:
                request.user.watchlist.add(listing)

        return redirect("listing", listing_id=listing.id)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": BidForm(),
        "comment_form": CommentForm(),
        "comments": listing.comments.all(),
        "is_owner": is_owner,
        "is_winner": is_winner,
        "in_watchlist": in_watchlist,
    })


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all()
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": category.listings.filter(active=True)
    })