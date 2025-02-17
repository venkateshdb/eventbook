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

    def __str__(self):
        return self.email


class Event(models.Model):

    event_id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=30, blank=False)
    description = models.TextField()
    header_img = models.CharField(max_length=35)
    status = models.CharField(max_length=10)  # Public/Private
    is_live = models.BooleanField()
    org_name = models.CharField(max_length=20)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    venue_name = models.CharField(blank=False, max_length=100)
    address = models.TextField(blank=False)
    city = models.CharField(blank=False, max_length=30)
    state = models.CharField(blank=False, max_length=30)
    country = models.CharField(blank=False, max_length=30)
    zip_code = models.IntegerField()

    quantity = models.IntegerField(blank=False)
    price = models.IntegerField()
    max_ticket = models.IntegerField(blank=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Event id:{0}, Title:{1}".format(
            self.event_id,
            self.title
        )


# class Location(models.Model):

#     loc_id = models.IntegerField(primary_key=True)
#     venue_name = models.CharField(blank=False, max_length=100)
#     address = models.TextField(blank=False)
#     city = models.CharField(blank=False, max_length=30)
#     state = models.CharField(blank=False, max_length=30)
#     country = models.CharField(blank=False, max_length=30)
#     zip_code = models.IntegerField()

#     event = models.ForeignKey(Event, on_delete=models.CASCADE)

#     def __str__(self):
#         return "Event id:{0}, Title:{1}".format(
#             self.event.event_id,
#             self.venue_name
#         )


class Images(models.Model):

    img_id = models.IntegerField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=30)

    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return "Event3:{0}, Image_id:{1}".format(
            self.event.title,
            self.img_id
        )

# class Category(models.Model):


# class Ticket(models.Model):

#     ticket_id = models.TextField(primary_key=True)
#     quantity = models.IntegerField(blank=False)
#     price = models.IntegerField()
#     max_ticket = models.IntegerField(blank=False)

#     event = models.ForeignKey(Event, on_delete=models.CASCADE)

#     def __str__(self):
#         return "Event3:{0}, ticket_id:{1}".format(
#             self.event.title,
#             self.ticket_id
#         )


class order_ticket(models.Model):

    payment_id = models.TextField(primary_key=True)
    order_id = models.TextField()
    signature = models.TextField()
    is_success = models.BooleanField()
    qty = models.IntegerField()

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
         return "Payment: {0}, User: {1}".format(
            self.payment_id,
            self.user.email
        )
