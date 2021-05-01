import random
import string
import os
import sys
from itertools import chain
from pathlib import Path
import json, base64
from PIL import Image
from pyzbar import pyzbar
from io import BytesIO
import qrcode

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt

from event.models import User, Event, pwd_context, order_ticket

from eventbook.settings import client

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = os.path.join(BASE_DIR, 'static')


def gen():
    return string.digits + string.ascii_letters


def id():
    """ generates random id's"""
    key = [random.choice(gen()) for i in range(6)]
    return "".join(key)


def index(request):

    get_event = Event.objects.all()

    context_dict = {
        "event": get_event
    }
    print(context_dict)
    return render(request, 'index.html', context=context_dict)


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
                request.session["email"] = get_user.email
                # messages.success(request, "Login Success !!")
                return redirect("create_event")
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
        # Get form data
        event_id = id()
        title = request.POST["title"]
        description = request.POST["description"]
        header_img = request.FILES["header_img"]
        status = request.POST["status"]
        is_live = True
        org_name = request.POST["org_name"]
        start_datetime = request.POST["start_datetime"]
        end_datetime = request.POST["end_datetime"]

        #Tickets
        qty = request.POST["qty"]
        price = request.POST["price"]
        max_qty = request.POST["max"]

        # Location data
        venue_name = request.POST["venue"]
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        country = request.POST["country"]
        zip_code = request.POST["zip_code"]

        user_id = request.session.get("user_id")

        user = User.objects.get(user_id=user_id)

        event = Event(event_id=event_id, title=title, description=description, header_img=header_img, status=status, is_live=is_live,
                      org_name=org_name, start_date_time=start_datetime, end_date_time=end_datetime, user=user,
                      venue_name=venue_name, address=address,
                       city=city, state=state, country=country, zip_code=zip_code, quantity=qty, price=price, max_ticket=max_qty)


        user.save()
        event.save()
        img = header_img.file
        file = os.path.join('static\\media', header_img.name)
        with open(file, 'wb') as outfile:
            outfile.write(img.getbuffer())
    context_dict = {
        "username": request.session.get("email").split('@')[0]
    }

    return render(request, 'create_event.html', context=context_dict)

@csrf_exempt
def event_details(request):
    """
    Manage event registration
    """
    if request.method == "POST":
        form = json.loads(request.body)

        data = {
            "amount" : 100 * int(form["amount"]), # Amount must be in paisa
            "currency": "INR",
            "receipt" : "order_" + id()
        }

        # Calls rzpay order API
        # @resp variable to be sent to client
        # side, for rzpay js initlization
        resp = client.order.create(data)

        # Check if user is logged in, if not register the user
        if request.session.get("logged_in"):
            resp['user'] = request.session.get("email")
        else:
            _id = id()
            email = form['email']
            password = form['pwd']
            resp['user'] = email
            User(user_id=_id, email=email,
                 password=pwd_context.hash(password)).save()
            request.session["user_id"] = _id

        resp["qty"] = form["qty"]
        request.session["ticket_qty"] = resp["qty"]
        return JsonResponse({'resp':resp})
    else:
        event_id = request.GET.get("event_id", '')

        request.session["event_id"] = event_id

        # Index to get data, as returns list.
        get_event = Event.objects.all().filter(event_id=event_id)[0]

        # create order_id
        context_dict = {
            "get_event": get_event
        }
        return render(request, 'event.html', context=context_dict)

def dashboard(request):
    user_id = request.session.get("user_id")

    get_event = Event.objects.all().filter(user_id=user_id)
    get_ticket = order_ticket.objects.select_related('event').select_related('user').filter(user_id=user_id)
    print(get_ticket.__dict__)
    # Create qr code
    # Format order_id|event_id|user_id
    for i in range(0, len(get_ticket)):
        encode_string = "{0}|{1}|{2}|{3}".format(get_ticket[i].order_id,get_ticket[i].event.event_id,get_ticket[i].user_id,get_ticket[i].user.email)
        print("encodee",encode_string)

        # Encoded string
        QR = qrcode.make(encode_string)

        # Create a buffer to store image
        buffer = BytesIO()
        QR.save(buffer,format='png')

        # convert to base64
        img_uri = base64.b64encode(buffer.getvalue())

        # Append img to each query
        get_ticket[i].img = img_uri.decode('utf-8')

    context_dict = {
        "events" : get_event,
        'tickets' : get_ticket
    }
    return render(request, 'dashboard.html', context=context_dict)

@csrf_exempt
def success(request):

    resp = request.POST

    payload = {
        "razorpay_payment_id" :resp["razorpay_payment_id"],
        "razorpay_order_id" : resp["razorpay_order_id"],
        "razorpay_signature" : resp["razorpay_signature"]
        }

    # Varibles for database operations
    user_id = request.session.get("user_id")
    event_id = request.session.get("event_id")
    qty = int(request.session.get("ticket_qty"))
    payment_id = resp["razorpay_payment_id"]
    order_id = resp["razorpay_order_id"]
    signature = resp["razorpay_signature"]

    get_user = User.objects.get(user_id=user_id)
    get_event = Event.objects.get(event_id=event_id)

    try:
        # This doent return anything, just an exception if signature
        # is incorrect hence use exception to deal with it
        client.utility.verify_payment_signature(payload)
        is_success = True
        # Store payment in database

        # reduce event tickets qty
        get_event.quantity -= qty
        payment = order_ticket(payment_id=payment_id, order_id=order_id, signature=signature, is_success=is_success,qty=qty, user=get_user,event=get_event)
        payment.save()
        get_event.save()
        return render(request,'success.html', {'status': "Payment Successful"})
    except:
        is_success = False
        payment = order_ticket(payment_id, order_id, signature, is_success, get_user,event=get_event)
        payment.save()
        return render(request,'success.html', {'status': "Payment Failed"})


@csrf_exempt
def qr_verify(request):
    if request.method == "POST":

        # convert bjson to string
        resp = json.loads(request.body.decode('utf-8'))

        try:
            # Get base64 img
            img = resp["img"].split(',')[1]

            # read image as png, and pass it to pyzbar to decode
            qr = Image.open(BytesIO(base64.b64decode(img)))
            qr_decode = (pyzbar.decode(qr)[0].data).decode('utf-8').split('|')

            """
            @Data Encode format
            @ Order_id|event_id|user_id
            """
            print(qr_decode)
            order_id = qr_decode[0]
            event_id = qr_decode[1]
            user_id = qr_decode[2]

            verify_qr = order_ticket.objects.select_related('event').select_related("user").filter(order_id=order_id)[0] #bug select related without user sending wrong user !!

            data = {
                "info" : {
                "order_id" : qr_decode[0],
                "event_id" : qr_decode[1],
                "user_id" : qr_decode[2],
                "pay_id" : verify_qr.payment_id,
                "user" : verify_qr.user.email,
                "event" : verify_qr.event.title,
                "qty" : verify_qr.qty,
                "paid" : verify_qr.is_success
                },
                "status": "success"
            }
            print(data)
            # print(order_id,event_id,user_id,json.dumps(data))
            return JsonResponse({"status": json.dumps(data)})
        except IndexError:
            return JsonResponse({"status": "QRError"})
    return render(request, 'qr.html')
