from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None, password2=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email, first_name, last_name, phone_number, password=None):
            user = self.create_user(
                email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number, 
                password=password,
            )
            user.is_admin = True
            user.save(using=self._db)
            return user

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at  = models.DateTimeField(auto_now = True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, null=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reset token for {self.user.username}"