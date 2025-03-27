from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            image = form.cleaned_data.get('image')

            # Prepare email
            email_message = EmailMessage(
                subject=f"New Contact Form Submission from {name}",
                body=message,
                from_email=email,
                to=['your-email@example.com'],  # Replace with your email
            )

            # Attach image if uploaded
            if image:
                email_message.attach(image.name, image.read(), image.content_type)

            # Send the email
            email_message.send()

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form})
