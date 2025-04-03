from django.shortcuts import (
    render,
    redirect,
    reverse,
    get_object_or_404,
    HttpResponse,
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from bag.contexts import bag_contents

import stripe
import json
import os


@require_POST
def cache_checkout_data(request):
    """
    Caches checkout data into Stripe's PaymentIntent metadata.

    This view is called during the checkout process to update the metadata
    of the Stripe PaymentIntent with the current session's shopping bag and
    user's information, which allows Stripe to reference this data when
    processing the payment.

    """
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "bag": json.dumps(request.session.get("bag", {})),
                "save_info": request.POST.get("save_info"),
                "username": request.user,
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            "Sorry, your payment cannot be processed right now."
            "Please try again later.",
        )
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    Handles the checkout process.

    This view is responsible for rendering the checkout page, processing
    the payment details, creating an order, and handling both successful
    and unsuccessful checkout attempts. It also interacts with Stripe's
    API to create a PaymentIntent for the transaction.

    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":
        bag = request.session.get("bag", {})

        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
            "county": request.POST["county"],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get("client_secret").split("_secret")[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        "One of the products in your bag"
                        "wasn't found in our database."
                        "Please call us for assistance!",
                    )
                    order.delete()
                    return redirect(reverse("view_bag"))

            request.session["save_info"] = "save-info" in request.POST
            return redirect(
                reverse("checkout_success", args=[order.order_number])
            )
        else:
            messages.error(
                request,
                "There was an error with your form."
                "Please double check your information.",
            )
    else:
        bag = request.session.get("bag", {})
        if not bag:
            messages.error(
                request, "There's nothing in your bag at the moment"
            )
            return redirect(reverse("products"))

        current_bag = bag_contents(request)
        total = current_bag["grand_total"]
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(
                    initial={
                        "full_name": profile.user.get_full_name(),
                        "email": profile.user.email,
                        "phone_number": profile.default_phone_number,
                        "country": profile.default_country,
                        "postcode": profile.default_postcode,
                        "town_or_city": profile.default_town_or_city,
                        "street_address1": profile.default_street_address1,
                        "street_address2": profile.default_street_address2,
                        "county": profile.default_county,
                    }
                )
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(
                request,
                "Stripe public key is missing."
                "Did you forget to set it in your environment?",
            )
            
          
        print(f"Current Bag: {current_bag}")
        print(f"Total from Bag: {total}")
        print(f"Stripe Total (in cents): {stripe_total}")


        template = "checkout/checkout.html"
        context = {
            "order_form": order_form,
            "stripe_public_key": stripe_public_key,
            "client_secret": intent.client_secret,
        }

        return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handles a successful checkout process.

    This view is called after a successful payment is made and is
    responsible for finalizing the order, saving the user profile data
    (if applicable), and sending confirmation emails to the user.
    """
    save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.town_or_city,
                "default_street_address1": order.street_address1,
                "default_street_address2": order.street_address2,
                "default_county": order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(
        request,
        f"Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.",
    )

    if "bag" in request.session:
        del request.session["bag"]

    template = "checkout/checkout_success.html"  # unused variable
    context = {  
     "order": order,
    }   

    # Read the subject and body from the confirmation email files
    subject_file_path = os.path.join(
        settings.BASE_DIR, "checkout", "templates", "checkout", "confirmation_emails", "confirmation_email_subject.txt"
    )
    body_file_path = os.path.join(
        settings.BASE_DIR, "checkout", "templates", "checkout", "confirmation_emails", "confirmation_email_body.txt"
    )

    # Read the content from the subject and body files
    try:
        with open(subject_file_path, "r") as subject_file:
            email_subject = subject_file.read().strip()

        with open(body_file_path, "r") as body_file:
            email_body = body_file.read().strip()
    except FileNotFoundError:
        email_subject = f"Order Confirmation - {order_number}"
        email_body = f"Hi {order.full_name},\n\nThank you for your order!"
        "Your order number is {order_number}."
        "We are processing your order and will update you when it ships."

    email_message = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )

    email_message.send()

    return render(request, "checkout/checkout_success.html", {"order": order})
