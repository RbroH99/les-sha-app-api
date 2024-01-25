"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Manager for the users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email!.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create superuser with given details."""
        user = self.model(email=email, password=password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = PhoneNumberField(max_length=16, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        """Returns the user string representation."""
        return self.email


class Product(models.Model):
    """Product object."""
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    types = models.ManyToManyField('Product_type', blank=True)

    def __str__(self):
        return self.name

    @property
    def rating(self):
        """Calculate average of product rating."""
        return self.rating_set.aggregate(models.Avg('value'))['value__avg']


class Product_type(models.Model):
    """Product type object."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Rating(models.Model):
    """Products rating object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(blank=False,
                                             null=False,
                                             validators=[MinValueValidator(1),
                                                         MaxValueValidator(5)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'],
                                    name='unique_rating'),
        ]

    def __str__(self):
        """Return rating string representation."""
        return f'{self.product.name}>{self.user.name}>{self.value}'
