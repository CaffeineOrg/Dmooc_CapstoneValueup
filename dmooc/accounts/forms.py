# from socket import fromshare
from dataclasses import field
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm


# from django.contrib.auth.hashers import check_password

# views.register에 사용
class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=64, label='ID')
    useremail = forms.EmailField(max_length=64, label='e-mail')

    class Meta:
        model = User
        fields = (
            'username',
            'useremail',
            'password1',
            'password2',
        )


class LoginForm(forms.Form):
    username = forms.CharField(error_messages={
        'required': '아이디를 입력하세요'}, max_length=64, label='사용자 아이디')
    password = forms.CharField(error_messages={
        'required': '비밀번호를 입력하세요'}, widget=forms.PasswordInput, label='비밀번호')

    # User 모델에서 기존 테이블을 불러와 Form에 들어온 데이터와 비교 작업
    def clean(self):
        clean_data = super().clean()
        username = clean_data.get('username')
        password = clean_data.get('password')

        if username and password:
            user = User.objects.get(username=username)
            # if not check_password(password, user.password):
            #     self.add_error('password', '비밀번호가 틀립니다')
            if not (password == user.password):
                self.add_error('password', '비밀번호가 틀립니다')
            else:
                self.user_id = user.pk