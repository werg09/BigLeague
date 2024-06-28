# railcar_management/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import Railcar , Tank
from .models import Customer , UserProfile , KosherWash
#from .models import Attachment

#from django.forms import widgets , FileField
#from bootstrap_datepicker_plus import DatePickerInput
from django.utils import timezone
#from django.forms import ClearableFileInput
#from crispy_forms.widgets import ClearableMultipleFileInput


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import StrictButton
from .models import Invoice , InvoiceItem

from django.forms import inlineformset_factory



User = get_user_model()

class UserProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    customer = forms.ModelChoiceField(queryset=Customer.objects.all())

    class Meta:
        model = UserProfile
        fields = ['user', 'customer']


class RailcarReleaseForm(forms.ModelForm):
    # Add a new field for displaying the customer name
    customer_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

     #Add a FileField for attachments
    attachments = forms.FileField(
        widget=forms.FileInput(),
        required=False,
    )

    class Meta:
        model = Railcar
        fields = ['railcar_number', 'received_date', 'track', 'customer', 'released_date','attachments']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # ... other fields
            Field('attachments'),
            StrictButton('Submit', type='submit'),
        )

        # Set default value for released_date
        current_time = timezone.localtime(timezone.now())  # Ensure it's localized
        self.fields['released_date'].widget.attrs['value'] = self.fields['released_date'].initial or current_time.strftime('%Y-%m-%d')

        # Populate the customer_name field with the current customer's name
        if self.instance and self.instance.customer:
            self.fields['customer_name'].initial = self.instance.customer.name

        # Hide the actual customer field
        self.fields['customer'].widget = forms.HiddenInput()

        # Make other fields read-only
        for field_name, field in self.fields.items():
            if field_name != 'customer':
                field.widget.attrs['readonly'] = True






class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username","email","password1","password2"]


class RailcarForm(forms.ModelForm):
    # Define a ModelChoiceField for the customer field
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), label='Customer')

    class Meta:
        model = Railcar
        fields = ['railcar_number', 'received_date', 'track', 'customer', 'net_weight', 'total_weight']

    def __init__(self, *args, **kwargs):
        super(RailcarForm, self).__init__(*args, **kwargs)
        # Customize the customer field to display customer names in the dropdown list
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['customer'].label_from_instance = lambda obj: f"{obj.name}"

class CustomerForm(forms.ModelForm):
    #user = forms.ModelChoiceField(queryset=User.objects.all())
    class Meta:
        model = Customer
        fields = ['name', 'entrance_fee', 'demurrage_rate', 'demurrage_free_days', 'customer_contact','customer_address','contact_email', 'rate_per_pound']

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if user is not None and hasattr(user, 'customer'):
            raise forms.ValidationError("This user is already associated with a customer.")
        return user

class RailcarEditForm(forms.ModelForm):
    class Meta:
        model = Railcar
        fields = ['railcar_number', 'received_date']  # Replace with your actual field names



class ProofOfPaymentForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['proof_of_payment']



class StandaloneInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'issue_date', 'due_date', 'customer', 'seller_name', 
            'seller_address', 'seller_contact', 'total_amount_due'
        ]



InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem, 
    fields=('description', 'quantity', 'price_per_unit'), 
    extra=1, 
    can_delete=True
)


class KosherWashForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tank'].choices = list(self.fields['tank'].choices) + [('CREATE_NEW', 'Create new tank...')]

    class Meta:
        model = KosherWash
        fields = ['driver_name', 'start_time', 'end_time', 'tank', 'wash_date', 'wash_duration', 'wash_type']


class TankForm(forms.ModelForm):
    class Meta:
        model = Tank
        fields = ['tank_number', 'capacity']  # replace with your actual fields