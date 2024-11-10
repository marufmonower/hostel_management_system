from django.db import models

class Room (models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField()
    occupied_beds = models.IntegerField(default = 0)
    
    def __str__(self):        
        return f"Room {self.room_number}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    nid = models.CharField(max_length=15)
    room = models.ForeignKey(Room,on_delete=models.SET_NULL,null=True)
    
    def __str__(self):
        return self.name
    
class Booking(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name="student_bookings")
    room = models.ForeignKey(Room,on_delete=models.CASCADE,related_name="room_bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.student.name} in {self.room.room_number}"
    