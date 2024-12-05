from django import forms
from .models import Room, Student, Booking, Payment,Expenditure
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'contact_number', 'nid', 'room']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'capacity', 'occupied_beds']


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
    overdue_amount = forms.DecimalField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        label="Overdue Amount (Read-only)"
    )
    class Meta:
        model = Payment
        fields = ['student',  # 'room',
                  'amount', 'currency', 'payment_date', 'status', 'due_date', 'reference','overdue_amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id', None)  # Get the selected student from the view
        super().__init__(*args, **kwargs)

        # Add an onchange event to reload the form with the selected student
        self.fields['student'].widget.attrs.update({
            'onchange': "location.href='?student=' + this.value;",
        })

        # Set the initial selected student (if available)
        if student_id:
            self.fields['student'].initial = student_id


class EditRoomForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['room']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
        }

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ['date','description','amount','category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
