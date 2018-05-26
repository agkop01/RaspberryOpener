from django.shortcuts import HttpResponse, redirect, render
from django.contrib.auth.forms import UserCreationForm
from .models import User

# Create your views here.

def index(request):
    return HttpResponse("<h1>You need to be logged to see the content.")

def home(request):
    return HttpResponse('<h1>Welcome to gate opener</h1>You are logged as:')

def profile(request):
    return HttpResponse("Welcome to Gate Opener")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile/')
    else:
        form = UserCreationForm()

        args = {'form': form}
        return render(request, 'accounts/reg_form.html', args)

