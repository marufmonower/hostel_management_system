from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Student, Room, Booking, Payment, Income, Expenditure
from .forms import StudentForm, RoomForm, BookingForm, PaymentForm, EditRoomForm, ExpenditureForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Max, F
from datetime import date
from django.contrib import messages
from django.http import Http404

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

        # Ensure object_list is set in POST requests
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
        if request.method == "POST":
            payment_form = PaymentForm(request.POST)
            student_id = request.POST.get('student_id')

            if payment_form.is_valid() and student_id:
                try:
                    student = get_object_or_404(Student, id=student_id)
                    payment = payment_form.save(commit=False)
                    payment.student = student
                    payment.save()
                    messages.success(request, "Payment added successfully!")
                    return redirect('student_list')
                except Http404:
                    messages.error(request, "Student not found.")

            messages.error(
                request, "Invalid form submission. Please check the details.")

        else:
            payment_form = PaymentForm()

        context = self.get_context_data()
        context['form'] = payment_form
        context['student_id'] = request.POST.get('student_id', None)
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

    def get_initial(self):
        initial = super().get_initial()

        overdue_amount = 0

        student_id = self.request.GET.get('student')
        if student_id:
            overdue_amount = Payment.objects.filter(
                student_id=student_id,
                due_date__lt=date.today(),
                status__in=['Pending', 'Overdue']
            ).aggregate(total_due=Sum('overdue_amount'))['total_due'] or 0

        initial['overdue_amount'] = overdue_amount
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-select the student if provided in GET request
        student_id = self.request.GET.get('student')
        if student_id:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['student'] = get_object_or_404(
                Student, id=student_id)
        return kwargs


@method_decorator(login_required, name='dispatch')
class PaymentUpdateView(UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/admin_edit_payment.html'
    success_url = reverse_lazy('admin_payment_list')


@login_required
def expenditure_list(request):
    expenditures = Expenditure.objects.all().order_by('-date')

    category = request.GET.get('category', '')
    if category:
        expenditures = expenditures.filter(category=category)

    search_query = request.GET.get('q', '')
    if search_query:
        expenditures = expenditures.filter(description__icontains=search_query)

    # Apply monthcode filter
    monthcode = request.GET.get('monthcode', '')
    if monthcode:
        expenditures = expenditures.filter(date__startswith=monthcode)

     # Generate unique monthcodes
    monthcodes = Expenditure.objects.annotate(
        month=TruncMonth('date')
    ).values_list('month', flat=True).distinct()
    formatted_monthcodes = [month.strftime(
        '%Y-%m') for month in monthcodes if month]

    # Calculate the total amount
    total_amount = expenditures.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'hostel/expenditure_list.html',
                  {'expenditures': expenditures,
                   'categories': Expenditure._meta.get_field('category').choices,
                   'total_amount': total_amount,
                   'monthcodes': formatted_monthcodes,
                   })


@login_required
def add_expenditure(request):
    if request.method == 'POST':
        form = ExpenditureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenditure_list')
    else:
        form = ExpenditureForm()
    return render(request, 'hostel/add_expenditure.html', {'form': form})


@login_required
def expenditure_summary(request):
    total_expenditure = Expenditure.objects.aggregate(Sum('amount'))[
        'amount__sum'] or 0
    category_wise = Expenditure.objects.values(
        'category').annotate(total=Sum('amount'))

    return render(request, 'hostel/expenditure_summary.html', {
        'total_expenditure': total_expenditure,
        'category_wise': category_wise
    })


@login_required
def income_list(request):
    incomes = Income.objects.all().order_by('-created_at')
    return render(request, 'income_list.html', {'incomes': incomes})


@login_required
def profit_summary(request):

    total_income = Income.objects.aggregate(Sum('amount__amount'))[
        'amount__amount__sum'] or 0
    total_expenditure = Expenditure.objects.aggregate(Sum('amount'))[
        'amount__sum'] or 0
    #payment_date = Payment.objects.filter

    # Apply monthcode filter
    monthcode = request.GET.get('monthcode', '')
    if monthcode:
        total_income = Income.objects.filter(payment_date__startswith=monthcode).aggregate(Sum('amount__amount'))[
            'amount__amount__sum'] or 0
        total_expenditure = Expenditure.objects.filter(created_at__startswith=monthcode).aggregate(Sum('amount'))[
            'amount__sum'] or 0

    # Generate unique monthcodes
    monthcodes = Expenditure.objects.annotate(
        month=TruncMonth('date')
    ).values_list('month', flat=True).distinct()
    formatted_monthcodes = [month.strftime(
        '%Y-%m') for month in monthcodes if month]

    profit = total_income - total_expenditure

    return render(request, 'hostel/profit_summary.html', {
        'total_income': total_income,
        'total_expenditure': total_expenditure,
        'profit': profit,
        'monthcodes': formatted_monthcodes,
    })


@login_required
def get_overdue_payments(request):

    # Annotate with the latest payment date (if applicable)
    payments_with_status = Payment.objects.annotate(
        last_payment_date=Max('payment_date')
    ).filter(
        due_date__lt=date.today(),  # Due date is earlier than today
        status__in=['Pending', 'Overdue']
    ).select_related('student', 'student__room')  # Ensure relationships exist

    # Calculate the total overdue amount
    total_due = payments_with_status.aggregate(
        total=Sum('overdue_amount')
    )['total'] or 0

    context = {
        'payments_with_status': payments_with_status,
        'total_due': total_due,
    }

    return render(request, 'hostel/overdue_report.html', context)
