from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Profile, Posts, Photo
from .forms import LoginForm, RegistrationForm, PostsForm

import random
import re


def index(request):

    """Главная страница"""

    if request.user.is_authenticated: return redirect('profile_page')

    else:

        count_profile = Profile.objects.count()
        count_posts = Posts.objects.count()

        data = {
            'title': 'Приветствие',
            'count_profile': count_profile,
            'count_posts': count_posts
        }

        return render(request, 'account/index.html', data)


@login_required(login_url='/')
def profile_page(request):

    """Профиль пользователя"""

    if request.method == 'POST':

        # кнопка новый аватар
        if 'nev_avatar' in request.FILES and request.FILES['nev_avatar']:

            person = Profile.objects.get(user=request.user.id)
            person.avatar = request.FILES['nev_avatar']
            person.save()

        # кнопка создать пост в ленте
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'create_post':

            content = request.POST['content']
            user = request.user

            Posts.objects.create(content=content, author=user)

        # кнопка загрузки фото
        if 'nev_photo' in request.FILES and request.FILES['nev_photo']:

            for send_photo in request.FILES.getlist('nev_photo'):

                photo = Photo()
                photo.author = request.user
                photo.photo = send_photo
                photo.save()

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    posts = Posts.objects.filter(author__username=request.user.username).order_by('-date')

    posts_form = PostsForm

    followers = Profile.objects.get(user=request.user.id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]
    random.shuffle(followers)
    followers = followers[:5]

    following = Profile.objects.get(user=request.user.id).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]
    random.shuffle(following)
    following = following[:5]

    all_photo = Photo.objects.filter(author__username=request.user.username).order_by('-date')

    photo_count = all_photo.count()

    all_photo_left = all_photo[:6][::-1]
    temp_left = [None for _ in range(6 - len(all_photo_left))]

    all_photo_right = all_photo[6:12]
    temp_right = [None for _ in range(6 - len(all_photo_right))]

    data = {
        'title': 'Моя страница:',
        'posts_form': posts_form,
        'user': user,
        'person': person,
        'posts': posts,
        'followers': followers,
        'following': following,
        'followers_count': followers_count,
        'following_count': following_count,
        'photo_count': photo_count,
        'all_photo_left': all_photo_left,
        'temp_left': temp_left,
        'all_photo_right': all_photo_right,
        'temp_right': temp_right,
    }

    return render(request, 'account/profile_page.html', data)


@login_required(login_url='/')
def profile_page_followers(request):

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=pk))

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    followers = Profile.objects.get(user=request.user.id).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    data = {
        'user': user,
        'person': person,
        'title': 'Мои подписчики:',
        'followers': followers,
        'followers_count': followers_count,
        'i_following': i_following,
    }

    return render(request, 'account/followers.html', data)


@login_required(login_url='/')
def profile_page_following(request):

    if request.method == 'POST':

        # кнопка отменить подписку
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    following = Profile.objects.get(user=request.user.id).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]

    data = {
        'user': user,
        'person': person,
        'title': 'Мои подписки:',
        'following': following,
        'following_count': following_count,
    }

    return render(request, 'account/following.html', data)


@login_required(login_url='/')
def profile_page_photo(request):

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=request.user.id)
    photo_all = Photo.objects.filter(author__username=request.user.username).order_by('-date')
    photo_tot = photo_all.count()

    data = {
        'user': user,
        'person': person,
        'title': 'Мои фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'account/profile_page_photo.html', data)


@login_required(login_url='/')
def profile_page_photo_show(request, pk_photo):

    user = f'{request.user.first_name} {request.user.last_name}'
    photo_single = Photo.objects.get(id=pk_photo)

    data = {
        'user': user,
        'title': 'Мои фотографии:',
        'photo_single': photo_single,
    }

    return render(request, 'account/profile_page_photo_show.html', data)


@login_required(login_url='/')
def another_user_page(request, pk):

    """Профиль другого пользователя"""

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=pk))

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=pk))

    if request.user.id != pk:

        user = f'{request.user.first_name} {request.user.last_name}'

        person = get_object_or_404(Profile, user=pk)                                            # профиль другого user
        posts = Posts.objects.filter(author__username=person.user).order_by('-date')            # посты другого user
        follower = person.followers.filter(username=request.user.username).exists()             # проверка подписки

        followers = Profile.objects.get(user=pk).followers.all()
        followers_count = followers.count()
        followers = [Profile.objects.get(profile_id=target.id) for target in followers]
        random.shuffle(followers)
        followers = followers[:5]

        following = Profile.objects.get(user=pk).following.all()
        following_count = following.count()
        following = [Profile.objects.get(profile_id=target.id) for target in following]
        random.shuffle(following)
        following = following[:5]

        all_photo = Photo.objects.filter(author__username=person.user).order_by('-date')

        photo_count = all_photo.count()

        all_photo_left = all_photo[:6][::-1]
        temp_left = [None for _ in range(6 - len(all_photo_left))]

        all_photo_right = all_photo[6:12]
        temp_right = [None for _ in range(6 - len(all_photo_right))]

        data = {
            'title': f'Пользователь #{pk}',
            'user': user,
            'person': person,
            'follower': follower,
            'posts': posts,
            'followers': followers,
            'following': following,
            'followers_count': followers_count,
            'following_count': following_count,
            'photo_count': photo_count,
            'all_photo_left': all_photo_left,
            'temp_left': temp_left,
            'all_photo_right': all_photo_right,
            'temp_right': temp_right,
        }

        return render(request, 'account/another_user_page.html', data)

    else: return redirect('profile_page')


@login_required(login_url='/')
def another_user_page_followers(request, pk):

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=user_pk))

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=user_pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    person = get_object_or_404(Profile, user=pk)  # профиль другого user

    followers = Profile.objects.get(user=pk).followers.all()
    followers_count = followers.count()
    followers = [Profile.objects.get(profile_id=target.id) for target in followers]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    data = {
        'user': user,
        'user_id': user_id,
        'person': person,
        'title': 'Подписчики:',
        'followers': followers,
        'followers_count': followers_count,
        'i_following': i_following,
    }

    return render(request, 'account/another_user_followers.html', data)


@login_required(login_url='/')
def another_user_page_following(request, pk):

    if request.method == 'POST':

        # кнопка подписаться
        if 'submit_button' in request.POST and request.POST['submit_button'] == 'follow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.follow(Profile.objects.get(profile_id=user_pk))

        # кнопка отменить подписку
        elif 'submit_button' in request.POST and request.POST['submit_button'] == 'unfollow':

            user_pk = request.POST['user_id']
            person = Profile.objects.get(profile_id=request.user.id)
            person.unfollow(Profile.objects.get(profile_id=user_pk))

    user = f'{request.user.first_name} {request.user.last_name}'
    user_id = request.user

    person = get_object_or_404(Profile, user=pk)  # профиль другого user

    following = Profile.objects.get(user=pk).following.all()
    following_count = following.count()
    following = [Profile.objects.get(profile_id=target.id) for target in following]

    i_following = Profile.objects.get(user=request.user.id).following.all()

    data = {
        'user': user,
        'user_id': user_id,
        'person': person,
        'title': 'Подписчики:',
        'followers': following,
        'followers_count': following_count,
        'i_following': i_following,
    }

    return render(request, 'account/another_user_following.html', data)


@login_required(login_url='/')
def another_user_page_photo(request, pk):

    user = f'{request.user.first_name} {request.user.last_name}'
    person = Profile.objects.get(user=pk)
    photo_all = Photo.objects.filter(author__username=person.user).order_by('-date')
    photo_tot = photo_all.count()

    data = {
        'user': user,
        'person': person,
        'title': 'Фотографии:',
        'photo_all': photo_all,
        'photo_tot': photo_tot,
    }

    return render(request, 'account/another_user_photo.html', data)


@login_required(login_url='/')
def another_user_page_photo_show(request, pk, pk_photo):

    user = f'{request.user.first_name} {request.user.last_name}'
    photo_single = Photo.objects.get(id=pk_photo)

    data = {
        'user': user,
        'title': 'Мои фотографии:',
        'photo_single': photo_single,
    }

    return render(request, 'account/another_user_photo_show.html', data)


@login_required(login_url='/')
def settings_page(request):

    """Страничка настроек / выход"""

    user = f'{request.user.first_name} {request.user.last_name}'

    data = {
        'title': 'Настройки',
        'user': user
    }

    return render(request, 'account/settings_page.html', data)


def login_page(request):

    """Страничка логирования"""

    error = ''

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')

        else:
            error = 'Данные не корректны, повторите ввод!'
            login_form = LoginForm

            data = {
                'title': 'Вход',
                'login_form': login_form,
                'error': error
            }

            return render(request, 'account/login_page.html', data)

    else:
        login_form = LoginForm

        data = {
            'title': 'Вход',
            'login_form': login_form,
            'error': error
        }

        return render(request, 'account/login_page.html', data)


def registration_page(request):

    """Страничка регистрации"""

    error = ''

    step1 = r"(?:[a-z0-9!#$%&'*+=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+=?^_`{|}~-]+)*)@(?:[a-z0-9]+(?:-[a-z0-9]+)*)\.[a-z]{2,5}"
    step2 = r"@.{1,63}\."

    def check_email(arg): return True if re.fullmatch(step1, arg) and re.search(step2, arg) else False

    if request.method == 'POST':

        registration_form = RegistrationForm(request.POST)

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        email = request.POST['email']
        username = email

        password = request.POST['password']
        password_confirmation = request.POST['password_confirmation']

        if User.objects.filter(username=username).exists():

            error = 'Пользователь с таким email уже существует!'
            registration_form = RegistrationForm

            data = {
                'title': 'Регистрация',
                'registration_form': registration_form,
                'error': error
            }

            return render(request, 'account/registration_page.html', data)

        elif registration_form.is_valid() and password == password_confirmation and check_email(email):

            User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)

            user = authenticate(request, username=username, password=password)
            login(request, user)

            return redirect('profile_page')

        else:

            error = 'Данные не корректны, повторите ввод!'
            registration_form = RegistrationForm

            data = {
                'title': 'Регистрация',
                'registration_form': registration_form,
                'error': error
            }

            return render(request, 'account/registration_page.html', data)

    else:
        registration_form = RegistrationForm

        data = {
            'title': 'Регистрация',
            'registration_form': registration_form,
            'error': error
        }

        return render(request, 'account/registration_page.html', data)


@login_required(login_url='/')
def logout_page(request):

    """Функция выхода для страницы настроек"""

    logout(request)
    return redirect('index')
