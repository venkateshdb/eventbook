from django.urls import path

from event import views

urlpatterns = [
    path('', views.index, name="index"),
    path('create', views.create_event, name="create event"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout")
]
