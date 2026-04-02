from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact(request):
    """Handle contact form submissions."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'your message has been sent. we will be in touch soon.'
            )
            return redirect('contact')
    else:
        if request.user.is_authenticated:
            form = ContactForm(
                initial={
                    'name': request.user.get_full_name(),
                    'email': request.user.email,
                },
                read_only_user=True,
            )
        else:
            form = ContactForm()

    template = 'contact/contact.html'
    context = {
        'form': form,
    }

    return render(request, template, context)