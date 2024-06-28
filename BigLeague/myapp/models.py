from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import models
from datetime import timedelta

# Create your models here.
# railcar_management/models.py


class Customer(models.Model):
    name = models.CharField(max_length=100)
    customer_address = models.CharField(max_length=255, null=True)
    customer_contact = models.CharField(max_length=255, null=True)
    entrance_fee = models.DecimalField(max_digits=10, decimal_places=2)
    demurrage_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    demurrage_free_days = models.PositiveIntegerField(default=0)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    rate_per_pound = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)


    def __str__(self):
        # Customize this method to return a meaningful representation of a customer
        return self.name  # Replace 'customer_name' with the actual field you want to display


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Railcar(models.Model):
    railcar_number = models.CharField(max_length=11)
    received_date = models.DateField()
    released_date = models.DateField(null=True, blank=True)
    released_timestamp = models.DateTimeField(null=True, blank=True)  # New field
    left_yard_date = models.DateField(null=True, blank=True)
    is_released = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    track = models.CharField(max_length=14, default='Default Track')
    net_weight = models.FloatField(null=True, blank=True)
    total_weight = models.FloatField(null=True, blank=True)

    def release(self):
        self.is_released = True
        self.released_date = timezone.now().date()
        self.released_timestamp = timezone.now()
        self.save()
    
    def calc_sugar_pound(self):
        if self.net_weight is not None and self.customer.rate_per_pound is not None:
            return self.net_weight * float(self.customer.rate_per_pound)
        else:
            return None

class ReleasedRailcar(models.Model):
    railcar = models.OneToOneField(Railcar, on_delete=models.CASCADE, primary_key=True)
    release_date = models.DateField()


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    railcar = models.ForeignKey('Railcar', related_name='attachments', on_delete=models.CASCADE, null=True, blank=True)


class DemurrageCharge(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    railcar = models.ForeignKey(Railcar, on_delete=models.CASCADE)
    demurrage_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    demurrage_days = models.IntegerField(default=0)

    def calculate_demurrage_rate(self):
        if self.railcar.is_released:
            total_days = (self.railcar.released_date - self.railcar.received_date).days
            self.demurrage_days = max(total_days - self.customer.demurrage_free_days, 0)
            customer_demurrage_rate = self.customer.demurrage_rate
            self.demurrage_charge = self.demurrage_days * customer_demurrage_rate
        else:
            self.demurrage_charge = 0
        self.save()
        return self.demurrage_charge#, self.demurrage_days  # Return the calculated value and demurrage_days # Return the calculated value and demurrage_days

class Invoice(models.Model):
    invoice_number = models.AutoField(primary_key=True)
    email_sent = models.BooleanField(default=False)
    issue_date = models.DateField()
    due_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    railcar = models.ForeignKey(Railcar, on_delete=models.CASCADE, null=True, blank=True)
    seller_name = models.CharField(max_length=255)
    seller_address = models.CharField(max_length=255)
    seller_contact = models.CharField(max_length=255)
    total_amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_timestamp = models.DateTimeField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    proof_of_payment = models.FileField(upload_to='proofs_of_payment/', null=True, blank=True)
    
    class Meta:
        unique_together = ('railcar', 'issue_date', 'due_date')
    

    def calculate_total_amount_due(self):
        demurrage_charge = self.railcar.demurragecharge.demurrage_charge if hasattr(self.railcar, 'demurragecharge') else 0
        entrance_fee = self.customer.entrance_fee
        self.total_amount_due = demurrage_charge + entrance_fee
        self.save()
        return self.total_amount_due  # Return the calculated value
    


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=5, decimal_places=2)




#Kosher wash releated models
class Tank(models.Model):
    tank_number = models.CharField(max_length=255)
    capacity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.tank_number)


class KosherWash(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    wash_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    driver_name = models.CharField(max_length=255)
    tank = models.ForeignKey(Tank, on_delete=models.CASCADE)
    wash_type = models.CharField(max_length=255)
    wash_duration = models.DurationField()
    expiration_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.expiration_date = self.wash_date + timedelta(days=6)
        super().save(*args, **kwargs)