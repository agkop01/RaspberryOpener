from django.shortcuts import HttpResponse, redirect, render
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.template import loader

# Create your views here.

def index(request):
    return HttpResponse("<h1>You need to be logged to see the content.")

def home(request):
    return render(request, 'accounts/home.html')

def profile(request):
    return render(request, 'accounts/profile.html')


def list(request):
    all_users = User.objects.all()
    template = loader.get_template('accounts/list.html')
    context = {
        'all_users' : all_users,
    }
    return HttpResponse(template.render(context, request))

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

def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile/')
    else:
        form = UserChangeForm(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/edit_profile.html', args)


def del_profile(request):
    if request.method == 'POST':
        form = User.objects.get(request.POST, instance=request.user)
        if form.is_valid():
            form.delete()
            return redirect('accounts/del_profile.html')
    else:
        form = User.objects.get(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/nouser.html', args)
