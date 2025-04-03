from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from .forms import ContactForm
from .models import ContactRequest  # Import the model to save the data


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
            # Extract cleaned data from the form
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            image = form.cleaned_data.get("image")

            # Prepare email
            email_message = EmailMessage(
                subject=f"New Contact Form Submission from {name}",
                body=message,
                from_email=email,
                to=["ameescook@gmail.com"],
            )

            # Attach image if it was uploaded
            if image:
                email_message.attach(
                    image.name, image.read(), image.content_type
                )

            # Send the email
            email_message.send()

            # Save the contact request in the database
            contact_request = ContactRequest(
                name=name, email=email, message=message, image=image
            )
            contact_request.save()

            # Display a success message to the user
            messages.success(
                request, "Your message has been sent successfully!"
            )

            # Redirect back to the contact page (or another page if you prefer)
            return redirect("contact")

    else:
        form = ContactForm()

    # Render the contact page with the form
    return render(request, "contact/contact.html", {"form": form})
