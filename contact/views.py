from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from .forms import ContactForm
from .models import ContactRequest  


def contact(request):
    """
    A view to handle the contact form submission. If the request is a /
    POST request,it processes the form data, sends an email with the user's /
    message and optional image, saves the request to the database, /
    and provides feedback to the user.
    """
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            image = form.cleaned_data.get("image")

            email_message = EmailMessage(
                subject=f"New Contact Form Submission from {name}",
                body=message,
                from_email=email,
                to=["ameescook@gmail.com"],
            )

            if image:
                email_message.attach(
                    image.name, image.read(), image.content_type
                )

            email_message.send()

            contact_request = ContactRequest(
                name=name, email=email, message=message, image=image
            )
            contact_request.save()

            messages.success(
                request, "Your message has been sent successfully!"
            )

            return redirect("contact")

    else:
        form = ContactForm()

    return render(request, "contact/contact.html", {"form": form})
