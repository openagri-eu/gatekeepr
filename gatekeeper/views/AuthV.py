import jwt
import logging
import os
from datetime import datetime, timedelta

from django.views.generic import TemplateView
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.urls import reverse, resolve, Resolver404
from django.http import HttpResponseRedirect

from gatekeeper.forms import LoginForm, RegisterForm, PasswordResetForm
from aegis.models import DefaultAuthUserExtend

logger = logging.getLogger('aegis')

# Secret keys for JWT encoding
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', 'default_access_token_secret')
REFRESH_TOKEN_SECRET = os.getenv('REFRESH_TOKEN_SECRET', 'default_refresh_token_secret')
JWT_SECRET = os.getenv('JWT_SECRET', 'default_jwt_secret')

print("ACCESS_TOKEN_SECRET:", ACCESS_TOKEN_SECRET)
print("REFRESH_TOKEN_SECRET:", REFRESH_TOKEN_SECRET)
print("JWT_SECRET:", JWT_SECRET)

# Token expiration times
ACCESS_TOKEN_EXPIRATION = timedelta(minutes=60)
REFRESH_TOKEN_EXPIRATION = timedelta(days=1)
JWT_EXPIRATION = timedelta(hours=1)


@method_decorator(never_cache, name='dispatch')
class LoginView(TemplateView):
    template_name = "auth/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            next_url = request.session.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('aegis:dashboard')

        next_url = request.GET.get('next', '')
        if next_url:
            request.session['next'] = next_url

        logger.info("Login view accessed")
        form = LoginForm(initial={'next': next_url})
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request, data=request.POST)
        next_url = request.session.get('next', '')
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Generate tokens
            access_token = self.generate_token(user.id, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_EXPIRATION)
            refresh_token = self.generate_token(user.id, REFRESH_TOKEN_SECRET, REFRESH_TOKEN_EXPIRATION)
            jwt_token = self.generate_token(user.id, JWT_SECRET, JWT_EXPIRATION)

            print(access_token)
            print(refresh_token)
            print(jwt_token)

            # Create response
            if 'farm_calendar' in next_url:
                response = HttpResponseRedirect('http://127.0.0.1:8002/test_perm')
            else:
                response = HttpResponseRedirect(next_url or 'aegis:dashboard')

            # Set cookies
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True)
            response.set_cookie('jwt', jwt_token, httponly=True)

            # Clear the next URL from session after successful login
            if next_url:
                del request.session['next']

            return response
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['next'] = next_url
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def is_valid_url(self, url):
        """
        Check if the URL is valid and can be resolved to a view.
        """
        try:
            resolve(url)
            return True
        except Resolver404:
            return False

    def generate_token(self, user_id, secret, expiration):
        """
        Generate a JWT token.
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + expiration,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, secret, algorithm='HS256')


@method_decorator(never_cache, name='dispatch')
class RegisterView(TemplateView):
    form_class = RegisterForm
    template_name = 'auth/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')  # Redirect to a success page.
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(never_cache, name='dispatch')
class PasswordResetView(TemplateView):
    template_name = 'auth/password_reset.html'
    form_class = PasswordResetForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            new_password = form.cleaned_data.get('new_password1')
            try:
                user = DefaultAuthUserExtend.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                logger.info("Password reset for user with email: {}".format(email))
                auth_login(request, user)
                return redirect('home')
            except DefaultAuthUserExtend.DoesNotExist:
                form.add_error('email', 'Email address not found.')

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)
