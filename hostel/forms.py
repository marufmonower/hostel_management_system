from django import forms
from .models import Room, Student, Booking
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'contact_number', 'nid', 'room']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'capacity','occupied_beds']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['student', 'room', 'start_date', 'end_date']
