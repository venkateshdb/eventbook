from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from event.models import User, Event, Location, pwd_context
import random
import string


def gen():
    return string.digits + string.ascii_letters


def id():
    """ generates random id's"""
    key = [random.choice(gen()) for i in range(6)]
    return "".join(key)


def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == "POST":
        # check for existing email
        email = request.POST["email"]
        try:
            User.objects.get(email=email)
            error = "User Already Exist"
        except ObjectDoesNotExist:
            password = request.POST["password"]
            User(user_id=id(), email=email,
                 password=pwd_context.hash(password)).save()
            messages.success(request, "signup successfull !!")
            return redirect("signup")
        else:
            messages.error(request, error)
            return redirect("signup")
    return render(request, "signup.html")


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            get_user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            error = "Invalid Credentials!"
            messages.error(request, error)
        else:
            if (get_user and pwd_context.verify(password, get_user.password)):
                request.session["logged_in"] = True
                request.session["user_id"] = get_user.user_id
                messages.success(request, "Login Success !!")
                return redirect("login")
            else:
                error = "Invalid Credentials!"
                messages.error(request, error)
    return render(request, "login.html")


def logout(request):
    request.session.clear()
    messages.success(request, "logged out")
    return redirect("login")


def create_event(request):
    if (request.session.get("logged_in") is None):
        messages.info(request, "You need to login first.")
        return redirect("login")

    if request.method == "POST":
        # Get from data
        event_id = id()
        title = request.POST["title"]
        description = request.POST["description"]
        header_img = request.FILES["header_img"]
        status = request.POST["status"]
        is_live = True
        org_name = request.POST["org_name"]
        start_date = request.POST["start_date"]
        start_time = request.POST["start_time"]
        end_date = request.POST["end_date"]
        end_time = request.POST["end_time"]
        start_date_time = start_date + ',' + start_time
        end_date_time = end_date + ',' + end_time

        # LOcation data
        venue_name = request.POST["venue"]
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        country = request.POST["country"]
        zip_code = request.POST["zip_code"]

        user_id = request.session.get("user_id")

        user = User.objects.get(user_id=user_id)

        event = Event(event_id=event_id, title=title, description=description, header_img=header_img, status=status, is_live=is_live,
                      org_name=org_name, start_date_time=start_date_time, end_date_time=end_date_time, user=user)

        loc = Location(venue_name=venue_name, address=address,
                       city=city, state=state, country=country, zip_code=zip_code, event=event)

        user.save()
        event.save()
        loc.save()

    return render(request, 'create_event.html')
