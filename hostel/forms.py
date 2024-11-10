from django import forms
from .models import Room, Student, Booking,Payment
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
        widgets = {
            'start_date': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'text', 'placeholder': 'DD/MM/YYYY'}),
            'end_date': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'text', 'placeholder': 'DD/MM/YYYY'}),
        }
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%d/%m/%Y']
        self.fields['end_date'].input_formats = ['%d/%m/%Y']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student','amount','currency','status','due_date','reference']
        widgets = {
            'amount':forms.NumberInput(attrs={'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }