from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.forms import UserRegisterForm
from main.models import CustomUser
from django.views import View
from django.contrib.auth.decorators import login_required

# Create your views here.

class RegistrationView(View):
    context = {}

    def get(self, request):
        form = UserRegisterForm()
        self.context['form'] = form
        return render(request, 'register.html', context=self.context)
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        print(request.POST.get('username'), request.POST.get('email'), request.POST.get('password1'), request.POST.get('password2'))
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Создан аккаунт {username}!')
            return redirect('profile')
        else:
            raise Http404


# @login_required
def profile(request):
    context = {}
    if request.user.is_authenticated:
        context['email'] = request.user.email
    return render(request, 'profile.html', context=context)