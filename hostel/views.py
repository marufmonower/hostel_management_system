from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Student, Room, Booking, Payment
from .forms import StudentForm, RoomForm, BookingForm, PaymentForm, EditRoomForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncMonth


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
    http_method_names = ['get', 'post']
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
    form_class = EditRoomForm

    def get_context_data(self, **kwargs):
        
         #Ensure object_list is set in POST requests
        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['PaymentForm'] = PaymentForm()
        return context

    def post(self, request, *args, **kwargs):

        if 'room' in request.POST:
            return self.update_room(request)
        elif 'amount' in request.POST:
            return self.add_payment(request)

    def update_room(self, request):
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        form = self.form_class(request.POST, instance=student)

        if form.is_valid():
            form.save()
            return redirect('student_list')

       # students = self.get_queryset()
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

    def add_payment(self, request):
        payment_form = PaymentForm(request.POST)
        student_id = request.POST.get('student_id')

        if payment_form.is_valid() and student_id:
            student = get_object_or_404(Student, id=student_id)
            payment = payment_form.save(commit=False)
            payment.student = student
            payment.save()
            return redirect('student_list')

        context = self.get_context_data()
        context['form'] = payment_form
        return self.render_to_response(context)


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


@method_decorator(login_required, name='dispatch')
class PaymentListView(ListView):
    model = Payment
    template_name = 'payments/admin_payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        queryset = super().get_queryset()

        monthcode = self.request.GET.get('monthcode')
        if monthcode:
            queryset = queryset.filter(payment_date__startswith=monthcode)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate a list of unique monthcodes
        monthcodes = Payment.objects.annotate(month=TruncMonth(
            'payment_date')).values_list('month', flat=True).distinct()
        formatted_monthcodes = [month.strftime(
            '%Y-%m') for month in monthcodes if month]

        # Pass the list of monthcodes to the template
        context['monthcodes'] = formatted_monthcodes
        return context


@method_decorator(login_required, name='dispatch')
class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/admin_add_payment.html'
    success_url = reverse_lazy('admin_payment_list')


@method_decorator(login_required, name='dispatch')
class PaymentUpdateView(UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/admin_edit_payment.html'
    success_url = reverse_lazy('admin_payment_list')
