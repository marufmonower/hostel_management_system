from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Student, Room, Booking
from .forms import StudentForm, RoomForm, BookingForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'hostel/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'hostel/login.html'


class CustomLogoutView(LogoutView):
    template_name = 'hostel/logout.html'
    next_page = reverse_lazy('home')


@method_decorator(login_required, name='dispatch')
class HomePageView(TemplateView):
    template_name = 'hostel/home.html'


@method_decorator(login_required, name='dispatch')
class RoomListView(ListView):
    model = Room
    template_name = 'hostel/room-list.html'
    context_object_name = 'rooms'


@method_decorator(login_required, name='dispatch')
class RoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hostel/room_form.html'
    success_url = reverse_lazy('room_list')


@method_decorator(login_required, name='dispatch')
class StudentListView(ListView):
    model = Student
    template_name = 'hostel/student_list.html'
    context_object_name = 'students'


@method_decorator(login_required, name='dispatch')
class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'hostel/student_form.html'
    success_url = reverse_lazy('student_list')


@method_decorator(login_required, name='dispatch')
class BookingListView(ListView):
    model = Booking
    template_name = 'hostel/booking_list.html'
    context_object_name = 'bookings'


@method_decorator(login_required, name='dispatch')
class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'hostel/booking_form.html'
    success_url = reverse_lazy('booking_list')
