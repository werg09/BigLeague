from django.shortcuts import render , redirect, HttpResponse , get_object_or_404
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.contrib.auth import login, logout, authenticate

from .models import Railcar, Customer , Attachment , DemurrageCharge , Invoice , InvoiceItem , KosherWash , Tank
from .forms import RailcarForm, CustomerForm , RailcarEditForm , RegisterForm , RailcarReleaseForm

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .tasks import send_email_with_sparkpost

#current_time = timezone.localtime(timezone.now())

#views
from django.contrib.auth.decorators import permission_required
from .forms import ProofOfPaymentForm

from .forms import UserProfileForm

from django.db import IntegrityError
from django.contrib import messages
from .forms import StandaloneInvoiceForm ,KosherWashForm ,TankForm

from django.shortcuts import redirect
from .forms import StandaloneInvoiceForm, InvoiceItemFormSet

from django.db.models import Exists, OuterRef

#DECORATOR FOR GROUPS
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='/login/')



#CREATE USER PROFILE
def create_user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('home')
            except IntegrityError:
                messages.error(request, 'This user is already assigned to another customer.')
    else:
        form = UserProfileForm()
    return render(request, 'main/create_user_profile.html', {'form': form})



# HOME PAGE
@login_required(login_url="/login")
def home(request):
    customer = None
    if hasattr(request.user, 'userprofile'):
        customer = request.user.userprofile.customer
        #customer = request.user.customer
    return render(request, 'main/home.html', {'user': request.user, 'customer': customer})


# OUTBOUND PAGE
@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def outbound(request):
    railcars = Railcar.objects.filter(is_released=True).order_by('-released_timestamp')
    invoices = Invoice.objects.filter(railcar_id=OuterRef('pk'))
    railcars = railcars.annotate(has_invoice=Exists(invoices))
    return render(request, 'main/outbound.html', {'railcars': railcars})

# RAILCAR RELEASE FORM COPY FOR PRINTING
@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def printable_railcar(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)
    customer = railcar.customer
    demurrage_charge = DemurrageCharge.objects.filter(railcar=railcar).first()
    print(f"DemurrageCharge instance: {demurrage_charge}")
    if demurrage_charge:
        demurrage_charge.calculate_demurrage_rate()
        print(f"Demurrage charge: {demurrage_charge.demurrage_charge}")
    total_days = (railcar.released_date - railcar.received_date).days
    return render(request, 'main/printable_railcar.html', {'railcar': railcar, 'demurrage_charge': demurrage_charge, 'customer': customer, 'total_days': total_days})



# BILLING PAGE / SHOWS ALL INVOICES
@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def billing(request):
    invoices = Invoice.objects.all().order_by('-invoice_number')
    return render(request, 'main/billing.html', {'invoices': invoices})



# SIGN UP PAGE
def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')

    else:
        form = RegisterForm()

    return render(request, "registration/sign_up.html", {'form': form})


# SHOWS ALL CUSTOMERS
@permission_required('myapp.view_customer', login_url='/login/')
@login_required(login_url="/login")
def customers_list(request):
    customers = Customer.objects.all()
    return render(request, 'main/customers_list.html', {'customers':customers})



# CREATE CUSTOMER
@permission_required('myapp.create_customer', login_url='/login/')
@login_required(login_url="/login")
def create_customer(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            customer = customer_form.save(commit=False)
            customer.save()
            return redirect('customers_list')
    else:
        customer_form = CustomerForm()

    return render(request, 'main/create_customer.html', {'customer_form':customer_form})



# EDIT CUSTOMER
@permission_required('myapp.change_customer', login_url='/login/')
@login_required(login_url="/login")
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'main/edit_customer.html', {'form': form, 'customer': customer})



# CUSTOMER DETAIL VIEW
@permission_required('myapp.view_customer', login_url='/login/')
@login_required(login_url="/login")
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'main/customer_detail.html', {'customer': customer})



# DELETE CUSTOMER
@permission_required('myapp.delete_customer', login_url='/login/')
@login_required(login_url="/login")
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customers_list')
    return render(request, 'main/delete_customer_confirm.html', {'customer': customer})




# SHOWS ALL RAILCARS IN YARD
@login_required(login_url="/login")
def railcar_list_in_yard(request):
    if request.user.is_superuser or request.user.groups.filter(name='Administrators').exists():
        railcars = Railcar.objects.filter(is_released=False) # Show all railcars in the yard if the user is an admin
    
    else:
        customer = request.user.userprofile.customer # Get the customer associated with the user
        railcars = Railcar.objects.filter(customer=customer, is_released=False) # Show only the customer's railcars in the yard
        
    return render(request, 'main/railcar_list_in_yard.html', {'railcars': railcars})


#CREATE RAILCAR / ADD RAILCAR
@permission_required('myapp.add_railcar', login_url='/login/')
@login_required(login_url="/login")
def create_railcar(request):
    if request.method == 'POST':
        railcar_form = RailcarForm(request.POST)
        if railcar_form.is_valid():
            railcar_form.save()
            return redirect('railcar_list_in_yard')  # Redirect to the railcar list page after creation 
    else:
        railcar_form = RailcarForm()

    return render(request, 'main/create_railcar.html', {'railcar_form': railcar_form })



#EDIT RAILCAR
@permission_required('myapp.change_railcar', login_url='/login/')
@login_required(login_url="/login")
def edit_railcar(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)
    if request.method == 'POST':
        form = RailcarEditForm(request.POST, instance=railcar)
        if form.is_valid():
            form.save()
            return redirect('railcar_detail', pk=pk) # Redirect to the detail view of the edited railcar
    else:
        form = RailcarEditForm(instance=railcar)
    return render(request, 'main/edit_railcar.html', {'form': form, 'railcar': railcar})



#RAILCAR DETAIL VIEW
@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def railcar_detail(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)
    return render(request, 'main/railcar_detail.html', {'railcar': railcar})


#DELETE RAILCAR
@login_required(login_url="/login")
def delete_railcar(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)

    if request.method == 'POST':
        # Confirming the deletion through a POST request
        railcar.delete()
        return redirect('railcar_list_in_yard')

    return render(request, 'main/delete_railcar_confirm.html', {'railcar': railcar})


# RAILCAR RELEASE / CHANGE RAILCAR STATUS
@permission_required('myapp.change_railcar', login_url='/login/')
@login_required(login_url="/login")
def release_railcar(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)
    
    if request.method == 'POST':
        form = RailcarReleaseForm(request.POST, request.FILES, instance=railcar)
        if form.is_valid():
            railcar = form.save(commit=False)
            railcar.is_released = True  # Set is_released to True
            railcar.released_timestamp = timezone.now()  # Set released_timestamp to current date and time
            railcar.save()

            # Create a DemurrageCharge instance for the released Railcar
            DemurrageCharge.objects.create(railcar=railcar, customer=railcar.customer)

            # checks if railcar is still in the yard 
            if not railcar.is_released:#if railcar is not released is a true condition, it checks
                yard_railcars = Railcar.objects.filter(is_released=False)
                if railcar in yard_railcars:
                    yard_railcars = yard_railcars.exclude(pk=railcar.pk)
                    # Redirect to railcar list if it was removed from the yard
                    return redirect('railcar_list_in_yard')

            # Save attachments
            for f in request.FILES.getlist('attachments'):
                Attachment.objects.create(file=f, railcar=railcar)

            return redirect('railcar_list_in_yard')
    else:
        form = RailcarReleaseForm(instance=railcar)

    return render(request,'main/release_railcar.html', {'form': form, 'railcar': railcar})


#UNDO RELEASE RAILCAR / CHANGE RAILCAR STATUS
@group_required('Superusers')
@login_required(login_url="/login")
def undo_release_railcar(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)
    railcar.is_released = False
    railcar.save()
    return redirect('railcar_list_in_yard')

#CREATE INVOICE / ADD INVOICE
@permission_required('myapp.add_invoice', login_url='/login/')
@login_required(login_url="/login")
def create_invoice(request, pk):
    railcar = get_object_or_404(Railcar, pk=pk)
    if Invoice.objects.filter(railcar_id=railcar.id).exists():
        return render(request, 'main/error.html', {'message': 'An invoice for this railcar already exists.'})
    
    # Ensure a DemurrageCharge object is associated with the Railcar object
    demurrage_charge = DemurrageCharge.objects.filter(railcar=railcar).first()
    if not demurrage_charge:
        demurrage_charge = DemurrageCharge.objects.create(
            customer=railcar.customer,
            railcar=railcar,
            demurrage_charge=0  # Set a temporary value for demurrage_charge
        )

    demurrage_charge.calculate_demurrage_rate()
    demurrage_days = demurrage_charge.demurrage_days  # Get demurrage_days from demurrage_charge

        # Calculate net_sugar_pound
    net_sugar_pound = railcar.calc_sugar_pound()
    if net_sugar_pound is not None:
        net_sugar_pound = Decimal(net_sugar_pound)

    invoice = Invoice.objects.create(
        issue_date=timezone.now(),
        due_date=timezone.now() + timedelta(days=15),  # Set due date to 30 days from now
        customer=railcar.customer,
        railcar=railcar,
        seller_name='FT & R Inc.',
        seller_address='9313 Billy the Kid St. El Paso, TX 79907',
        seller_contact='Sally Flores',
        total_amount_due=demurrage_charge.demurrage_charge + railcar.customer.entrance_fee + (net_sugar_pound if net_sugar_pound else 0)  # Calculate total_amount_due here
    )
    
    print(invoice.customer.customer_address)
    print(invoice.customer.customer_contact)
    return render(request, 'main/invoice_detail.html', {'invoice': invoice, 'demurrage_charge': demurrage_charge, 'demurrage_days': demurrage_days, 'net_sugar_pound': net_sugar_pound})# Redirect to the detail view of the created invoice


@login_required(login_url="/login")
def send_invoice(request, invoice_number):
    # Get the invoice
    invoice = Invoice.objects.get(invoice_number=invoice_number)

    # Create the invoice data dictionary
    invoice_data = {
        'invoice_number': invoice.invoice_number,
        'issue_date': str(invoice.issue_date),
        'due_date': str(invoice.due_date),
        'customer_name': invoice.customer.name,
        'customer_address': invoice.customer.customer_address,
        'customer_contact': invoice.customer.customer_contact,
        'seller_name': invoice.seller_name,
        'seller_address': invoice.seller_address,
        'seller_contact': invoice.seller_contact,
        'total_amount_due': str(invoice.total_amount_due),
        # Add any other fields you want to include in the email
    }

    if invoice.railcar is not None:
        invoice_data['railcar_id'] = invoice.railcar.id
        invoice_data['demurrage_charge'] = str(invoice.railcar.demurragecharge_set.first().demurrage_charge)
    
    if invoice.customer.entrance_fee is not None:
        invoice_data['entrance_fee'] = str(invoice.customer.entrance_fee)

    # Get the customer's email
    to_email = invoice.customer.contact_email

    # Set the from email, subject, and text
    from_email = 'accounting@ferzatruckandrails.com'
    subject = 'Your Invoice'
    text = 'Hello, here is your invoice.'

    print(invoice_data)

    # Send the email
    send_email_with_sparkpost.delay(to_email, from_email, subject, text, invoice_data)

    # Mark the invoice as emailed
    invoice.email_sent = True
    invoice.save()

    # Render the send_invoice template
    return render(request, 'main/send_invoice.html')



@permission_required('myapp.view_invoice', login_url='/login/')
@login_required(login_url="/login")
def invoice_final(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    
    railcar = invoice.railcar
    if railcar is not None:
        customer = railcar.customer
        demurrage_charge = DemurrageCharge.objects.filter(railcar=railcar).first()
        if demurrage_charge:
            demurrage_charge.calculate_demurrage_rate()
        total_days = (railcar.released_date - railcar.received_date).days
        charged_days = max(0, total_days - customer.demurrage_free_days)  # Subtract free days from total days
        net_sugar_pound = railcar.calc_sugar_pound()
        return render(request, 'main/invoice_final.html', {'invoice': invoice, 'demurrage_charge': demurrage_charge, 'customer': customer, 'total_days': total_days, 'net_sugar_pound': net_sugar_pound, 'charged_days': charged_days})
    else:
        items = InvoiceItem.objects.filter(invoice=invoice)
        return render(request, 'main/invoice_final.html', {'invoice': invoice, 'items': items , })
    



def unpaid_invoice(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    return render(request, 'main/unpaid_invoice.html', {'invoice': invoice})



def upload_proof(request, invoice_number):
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
    if request.method == 'POST':
        form = ProofOfPaymentForm(request.POST, request.FILES, instance=invoice)
        if form.is_valid():
            invoice.is_paid = True  # Set is_paid to True
            print(f"Invoice {invoice.invoice_number} is_paid: {invoice.is_paid}")  # Print is_paid status
            form.save()
            return redirect('billing')
    else:
        form = ProofOfPaymentForm(instance=invoice)
    return render(request, 'main/payment_proof.html', {'form': form})






def create_standalone_invoice(request):
    if request.method == 'POST':
        form = StandaloneInvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.invoice = invoice
                item.save()
            return redirect('view_standalone_invoice', invoice_id=invoice.invoice_number)
    else:
        form = StandaloneInvoiceForm()
        formset = InvoiceItemFormSet(prefix='items')

    return render(request, 'main/create_standalone_invoice.html', {'form': form, 'formset': formset})



def view_standalone_invoice(request, invoice_id):
    invoice = Invoice.objects.get(invoice_number=invoice_id)
    print(invoice.issue_date, invoice.total_amount_due, invoice.invoiceitem_set.all())  # Corrected line
    return render(request, 'main/view_standalone_invoice.html', {'invoice': invoice})


@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def railcar_search(request):
    search_query = request.GET.get('search', '')
    railcars = Railcar.objects.filter(railcar_number=search_query)
    return render(request, 'main/railcar_profile.html', {'railcars': railcars})


@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def kosher_wash_list(request):
    kosher_wash = KosherWash.objects.all().order_by('-created_at')
    #kosher_wash = KosherWash.objects.all().order_by('-end_time')
    #kosher_wash = KosherWash.objects.filter(wash_date=timezone.now().date()).order_by('-end_time')
    
    return render(request, 'main/kosher_wash_list.html', {'kosher_wash': kosher_wash})



@permission_required('myapp.view_railcar', login_url='/login/')
@login_required(login_url="/login")
def inbound_railcar_list(request):
    railcars = Railcar.objects.filter(is_released=True).order_by('-released_timestamp')
    invoices = Invoice.objects.filter(railcar_id=OuterRef('pk'))
    railcars = railcars.annotate(has_invoice=Exists(invoices))
    return render(request, 'main/inbound_railcar_list.html', {'railcars': railcars})

@permission_required('myapp.view_railcar', login_url='/login/')
def create_kosher_wash(request):
    if request.method == 'POST':
        form = KosherWashForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kosher_wash_list')
    else:
        form = KosherWashForm()
    return render(request, 'main/create_kosher_wash.html', {'form': form})



@permission_required('myapp.view_railcar', login_url='/login/')
def create_tank(request):
    if request.method == 'POST':
        form = TankForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_kosher_wash')  # redirect back to the kosher wash form
    else:
        form = TankForm()
    return render(request, 'main/create_tank.html', {'form': form})

@permission_required('myapp.view_railcar', login_url='/login/')
def view_all_tanks(request):
    tanks = Tank.objects.all()
    return render(request, 'main/view_all_tanks.html', {'tanks': tanks})


@permission_required('myapp.view_railcar', login_url='/login/')
def delete_tank(request, tank_id):
    tank = get_object_or_404(Tank, id=tank_id)
    tank.delete()
    return redirect('view_all_tanks')

def kosherwash_detail(request, pk):
    kosherwash = get_object_or_404(KosherWash, pk=pk)
    return render(request, 'main/kosherwash_detail.html', {'kosherwash': kosherwash})

#from django.contrib.auth.models import Group
#groups = Group.objects.all()
#for group in groups:
    #print(f"Group: {group.name}")
    #print("Members:")
    #for user in group.user_set.all():
        #print(f"- {user.username}")
        #print("Permissions:")
    #for perm in group.permissions.all():
        #print(f"- {perm.codename}")