from django.db import models
from passlib.context import CryptContext


# Password hash management
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "des_crypt"]
)


class User(models.Model):

    user_id = models.CharField(max_length=5, primary_key=True)
    email = models.EmailField(blank=False)
    password = models.TextField(blank=False)


class Event(models.Model):

    event_id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=30, blank=False)
    description = models.TextField()
    header_img = models.CharField(max_length=35)
    status = models.CharField(max_length=10)  # Public/Private
    is_live = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Location(models.Model):

    venue_name = models.CharField(blank=False, max_length=100)
    address = models.TextField(blank=False)
    city = models.CharField(blank=False, max_length=30)
    state = models.CharField(blank=False, max_length=30)
    country = models.CharField(blank=False, max_length=30)
    zip_code = models.IntegerField()

    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Images(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=30)

# class Category(models.Model):


class Organizer(models.Model):

    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    org_name = models.CharField(max_length=20)
