from django.db import models
import uuid
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import tree
import stripe
from django.conf import settings
# Create your models here.


class UserManager(BaseUserManager):
  
    def create_user(self, email, password=None, name=None, academy=0):
        """
        Create and return a `User` with an email, username and password.
        """
        if not email:
            raise ValueError('Users Must Have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.name = name
        user.academy = academy
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
        )
    usertype = models.IntegerField(default=0)
    name =  models.CharField(max_length=50, unique=False, blank=True, null=True)
    academy = models.IntegerField(blank=True, null=True)
    avatar =  models.CharField(max_length=255, unique=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    is_superuser = models.BooleanField(default=False)

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()
    def __str__(self):
        return self.email

    class Meta:
        db_table = "User"