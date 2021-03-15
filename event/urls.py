from django.urls import path
from django.conf.urls import url
from event import views

urlpatterns = [
    path('', views.index, name="index"),
    path('create', views.create_event, name="create_event"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('e/', views.event_details, name="event_details"),
    path('success/', views.success, name="success"),
]
