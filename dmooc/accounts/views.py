import re
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .models import User
# from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm, RegisterForm


def home(request):
    user_id = request.session.get('user')
    if user_id:
        user = User.objects.get(pk=user_id)
        return HttpResponse("%s님이 로그인하였습니다." % user)
    else:
        return HttpResponse("로그인 해주세요!")


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        msg = '잘못 입력하였습니다'
        if form.is_valid():  # username, pw1, pw2가 입력 되었으면
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            msg = '회원가입 완료'
        return render(request, 'register.html', {'form': form, 'msg': msg})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})


# 로그인
def login_view(request):
    if request.method == 'POST':
        # 유저 존재하는지 검증
        form = AuthenticationForm(request, request.POST)  # Django가 만들어 놓은 Form
        msg = '가입되어 있지 않거나 로그인 정보가 잘못되었습니다.'
        print(form.is_valid)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                msg = 'login success!'
                login(request, user)
        return render(request, 'login.html', {'form': form, 'msg': msg})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})


# 로그아웃
def logout_view(request):
    logout(request)
    return redirect('index')