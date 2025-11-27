from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=100, default='user')
    login = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    portfolios_created = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    profile_image = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return self.login