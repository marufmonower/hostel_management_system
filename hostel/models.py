from django.db import models
from datetime import date
from django.contrib.auth.models import User
import calendar


class Room (models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField()
    occupied_beds = models.IntegerField(default=0)

    def __str__(self):
        return f"Room {self.room_number}"


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    nid = models.CharField(max_length=15)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_bookings")
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="room_bookings")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.student.name} in {self.room.room_number}"


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), (
        'Completed', 'Completed'), ('Overdue', 'Overdue')], default='Pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_due = models.BooleanField(default=False)
    overdue_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=255, blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    oprstamp = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    @property
    def monthcode(self):
        # Returns the monthcode as YYYY-MM format
        return self.payment_date.strftime('%Y-%m')

    def save(self, *args, **kwargs):
        if not self.room_number:
            try:
                hostel_student = Student.objects.get(name=self.student)
                self.room_number = hostel_student.room
            except Student.DoesNotExist:
                self.room_number = 'Unknown'  # Default value if the student is not found

        if self.payment_date:
            last_day_of_month = calendar.monthrange(
                self.payment_date.year, self.payment_date.month)[1]
            self.due_date = self.payment_date.replace(day=last_day_of_month)

        if self.due_date and date.today() > self.due_date.date() and self.status != 'Completed':
            # if self.due_date < date.today() and self.status != 'Completed':
            self.status = 'Overdue'
            self.is_due = True
        # set overdue_amount to the total amount if overdue
            self.overdue_amount = self.amount
        else:
            self.is_due = False
            self.overdue_amount = 0.00

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name}-{self.amount}{self.currency}"


class Expenditure(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=255)
    # amount = models.OneToOneField(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, choices=[
        ('Maintenance', 'Maintenance'),
        ('Electric_bill', 'Electric_bill'),
        ('Swiper_bill', 'Swiper_bill'),
        ('Paper_bill', 'Paper_bill'),
        ('Internet_bill', 'Internet_bill'),
        ('Miscellaneous', 'Miscellaneous')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def monthcode(self):
        # Returns the monthcode as YYYY-MM format
        return self.date.strftime('%Y-%m')

    def __str__(self):
        return f"{self.date}-{self.description}-{self.amount}"


class Income(models.Model):
    amount = models.OneToOneField(Payment, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=[
        ('Rent', 'Rent'),
        ('Other', 'Other'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def monthcode(self):
        # Returns the monthcode as YYYY-MM format
        return self.date.strftime('%Y-%m')

    def __str__(self):
        return f"Income from {self.payment.description} - {self.payment.amount}"
