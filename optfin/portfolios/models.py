from django.db import models
from registration.models import User

class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    risk = models.CharField(max_length=50)
    annual_return = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Portfolio {self.id} ({self.user.login})"
