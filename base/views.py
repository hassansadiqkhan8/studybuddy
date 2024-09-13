from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm



# Login Page
def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist.")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or Password is incorrect.")

    return render(request, "base/login_register.html", {"page":page})


# Logout User
def logoutUser(request):
    logout(request)
    return redirect("home")


# Register Page
def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error ocurred during registration.")

    return render(request, "base/login_register.html", {"form":form})


# Home Page
def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    return render(request, "base/home.html", {"rooms": rooms, "topics":topics, "room_count":room_count, "room_messages":room_messages})


# Rooms Page
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    return render(request, "base/room.html", {"room": room, "room_messages":room_messages, "participants":participants})


# User Profile
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    return render(request, "base/profile.html", {"user":user, "rooms":rooms, "room_messages": room_messages, "topics": topics})


# Creating a new Room
@login_required(login_url="login")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    return render(request, "base/room_form.html", {"form": form, "topics":topics})


# Updating Room
@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed to do that!!!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    return render(request, "base/room_form.html", {"form":form, "topics": topics, "room":room})


# Deleting Room
@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to do that!!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": room})


# Deleting Messages
@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to do that!!!")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": message})


# Update User Profile
@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
        else:
            messages.error(request, "Wrong username or email try again...")

    return render(request, "base/update_user.html", {"form": form})