from django.urls import path
from .import views
from .views import register,CustomLogoutView,RoomListView, RoomCreateView, StudentListView, StudentCreateView, BookingListView, BookingCreateView, CustomLoginView,PaymentListView,PaymentCreateView,PaymentUpdateView

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
    path('payments/', PaymentListView.as_view(), name='admin_payment_list'),
    path('payments/add', PaymentCreateView.as_view(), name='admin_add_payment'),
    path('payments/edit/<int:pk>', PaymentUpdateView.as_view(), name='admin_edit_payment'),
    path('expenditures/', views.expenditure_list, name='expenditure_list'),
    path('expenditures/add/', views.add_expenditure, name='add_expenditure'),
    path('expenditures/summary/', views.expenditure_summary, name='expenditure_summary'),
    path('profit/', views.profit_summary, name='profit_summary'),
    path('overdue_payments/', views.get_overdue_payments, name='overdue_payments'),
]
