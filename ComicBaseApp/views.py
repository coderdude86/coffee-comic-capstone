from django.shortcuts import HttpResponseRedirect, reverse, render
from django.contrib.auth import login, authenticate, logout
from django.views.generic import View, FormView
from ComicBaseApp.models import ComicComment, ComicUser, ComicBook
from ComicBaseApp.forms import CommentForm, SignUpForm, LoginForm


import requests
import environ

env = environ.Env()
environ.Env.read_env()


class AddCommentView(FormView):
    def get(self, request):
        template_name = 'form.html'
        form = CommentForm()
        return render(request, template_name, {'form': form})

    def post(self, request):
        form = CommentForm(request.POST)
        if form.is_valid():
            post_user = ComicUser.objects.filter(
                username=request.user.username).first()
            # fix to be preselected on click
            post_comic = ComicBook.objects.all().first()
            data = form.cleaned_data
            new_comment = ComicComment.objects.create(
                comment=data['comment'],
                user=post_user,
                comic_book_title=post_comic
            )
            return HttpResponseRedirect(reverse('home'))


class SignupView(View):
    def get(self, request):
        template_name = 'form.html'
        form = SignUpForm()
        return render(request, template_name, {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_user = ComicUser.objects.create_user(
                username=data['username'],
                password=data['password']
            )
            login(request, new_user)
            return HttpResponseRedirect(reverse("home"))


class LoginView(View):
    def get(self, request):
        template_name = 'form.html'
        form = LoginForm
        return render(request, template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request,
                username=data.get('username'),
                password=data.get('password')
            )
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))



def index(request):
    html = 'index.html'
    BASE_URL = 'https://comicvine.gamespot.com/api/'
    END_POINT = 'character/4005-75254/'
    QUERY = '' 
    url = f"{BASE_URL}{END_POINT}?format=json&api_key={env('API_KEY')}&{QUERY}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    info = response.json()
    issue_results = info['results']
    context = {'issue': issue_results}
    return render(request, html, context)

def e404(request, exception):
    html = '404.html'
    response = (render(request, html))
    response.status_code = 404
    return response

def e500(request):
    html = '500.html'
    response = (render(request, html))
    response.status_code = 500
    return response