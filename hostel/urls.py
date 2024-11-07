from django.urls import path
from .import views
from .views import register,CustomLogoutView,RoomListView, RoomCreateView, StudentListView, StudentCreateView, BookingListView, BookingCreateView, CustomLoginView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(),name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', views.HomePageView.as_view(), name='home'),
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/add/', RoomCreateView.as_view(), name='room_add'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/add/', StudentCreateView.as_view(), name='student_add'),
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('booking/add', BookingCreateView.as_view(), name='booking_add'),
]
