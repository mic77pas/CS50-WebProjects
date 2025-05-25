from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like


def index(request):
    return render(request, "network/index.html")


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def create_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "")
        if content:
            post = Post(user=request.user, content=content)
            post.save()
            return JsonResponse({"message": "Post created successfully."}, status=201)
    return JsonResponse({"error": "Invalid request"}, status=400)


def all_posts(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        "posts": [post.serialize() for post in page_obj],
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "total_posts": posts.count()  # Add total_posts to your response
    }, safe=False)
    
    
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        followers = user.followers.count()
        following = user.following.count()
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        posts = Post.objects.filter(user=user).order_by("-timestamp")
        
        return JsonResponse({
            "username": user.username,
            "followers": followers,
            "following": following,
            "is_following": is_following,
            "posts": [post.serialize() for post in posts]
        })
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    

@csrf_exempt
@login_required
def follow_toggle(request, username):
    try:
        target = User.objects.get(username=username)
        if request.user == target:
            return JsonResponse({"error": "Cannot follow yourself."}, status=400)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            follow.delete()
            return JsonResponse({"message": "Unfollowed."})
        return JsonResponse({"message": "Followed."})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    

@login_required
def following_posts(request):
    user = request.user
    following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    
    # Paginate results
    page_number = request.GET.get("page", 1)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        "posts": [post.serialize() for post in page_obj],
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "total_posts": posts.count(),  # Add total_posts to the response
    })
    

@csrf_exempt
@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id, user=request.user)
        if request.method == "PUT":
            data = json.loads(request.body)
            post.content = data.get("content", post.content)
            post.save()
            return JsonResponse({"message": "Post updated."})
        return JsonResponse({"error": "PUT request required."}, status=400)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found or not yours."}, status=404)
    
    
@csrf_exempt
@login_required
def like_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        liked = Like.objects.filter(user=request.user, post=post)
        if liked.exists():
            liked.delete()
            return JsonResponse({"message": "Unliked", "likes": post.likes.count()})
        else:
            Like.objects.create(user=request.user, post=post)
            return JsonResponse({"message": "Liked", "likes": post.likes.count()})
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)