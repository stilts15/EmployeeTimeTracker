from django.db import models

from django.contrib.auth.models import User


class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Restaurant: {self.name} | Owner: {self.owner}'
    

class Employee(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    active_session = models.BooleanField(default=False)
    active_service = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Employee: {self.name} | Restaurant: {self.restaurant}'
    
    
class Session(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField(null=True, blank=True)

    def working_hours(self):
        if self.start_time and self.stop_time:
            delta = self.stop_time - self.start_time
            hours = delta.total_seconds() / 3600  # Convert seconds to hours
            return round(hours, 1)  # Round to 1 decimal place
        return None
    
    def __str__(self):
        return f'Employee: {self.employee} | Start: {self.start_time} | Stop: {self.stop_time}'
    