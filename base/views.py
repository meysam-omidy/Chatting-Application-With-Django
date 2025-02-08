import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import myUserCreationForm, profileForm, groupCreationForm, imageForm, groupImageForm
from .models import User, message, Group, groupMessage, status, Request, Theme, image_message, group_image_message
from django.views.decorators.csrf import csrf_protect
import json,os

@login_required(login_url='login_user')
def home(request):
    user = User.objects.get(id=request.user.id)
    messages = message.objects.all()
    if request.GET.get('message_to') is not None:
        friend = User.objects.get(id=int(request.GET.get('message_to')))
        check = False
        for x in user.friends.all():
            if x.id == friend.id:
                check = True
                break
        if not check:
            return redirect('home')
        if request.method == 'POST':
            message.objects.create(
                text=request.POST.get("message"),
                sender=user,
                receiver=friend,
                seen="no",
            )
            return redirect('/?message_to=' + friend.id)
        else:
            return render(request, 'main.html', {'user': user, 'friend': friend, 'messages': messages, 'page': 'chat',
                                                 'user_theme': user.theme, 'form':imageForm})

    elif request.GET.get('group') is not None:
        users = User.objects.all()
        group = Group.objects.get(id=request.GET.get('group'))
        allowed = False
        for x in group.participants.all():
            if x.username == request.user.username:
                allowed = True
                break
        if not allowed and not group.is_public:
            return redirect('home')
        if request.method == 'POST':
            if request.POST.get('message') is not None:
                m = groupMessage.objects.create(
                    text=request.POST.get('message'),
                    sender=request.user,
                    receiver=Group.objects.get(id=request.GET.get('group')),
                )
                return redirect('/?group=' + request.GET.get('group'))
            else:
                group.participants.add(request.user)
                return redirect('/?group=' + request.GET.get('group'))
        # else:
        #     allowed = True
        #     try:
        #         group.participants.all().get(username=request.user.username)
        #     except:
        #         allowed = False
        #     return render(request, 'main.html', {'user': user,
        #                                          'qs_json': json.dumps(list(User.objects.values()), default=str),
        #                                          'page': 'group', 'users': User, 'group': group, 'allowed': allowed})
        return render(request, 'main.html',
                      {'user': user, 'group': group, 'page': 'group', 'allowed': allowed, 'user_theme': user.theme})
    else:
        return render(request, 'main.html', {'user': user, 'messages': messages,
                                             'qs_json': json.dumps(list(User.objects.values()), default=str),
                                             'page': 'none', 'user_theme': user.theme})


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login_register.html',
                              {'error': 'username or password is incorrect', 'page': 'login'})
        except:
            return render(request, 'login_register.html', {'error': 'username does not exist', 'page': 'login'})
    else:
        return render(request, 'login_register.html', {'page': page})


def registerUser(request):
    if request.user.is_authenticated:
        return redirect('home')
    page = 'register'
    if request.method == 'POST':
        form = myUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.theme = Theme.objects.get(name='main')
            user.save()
            login(request, user)
            status.objects.create(user_id=user.id)
            return redirect('home')
        else:
            return render(request, 'login_register.html',
                          {'error': 'something went wrong', 'page': 'register', 'form': myUserCreationForm()})
    else:
        return render(request, 'login_register.html', {'page': page, 'form': myUserCreationForm()})


def logoutUser(request):
    logout(request)
    return redirect('login_user')


@login_required(login_url='login_user')
def profile(request, pk):
    user = User.objects.get(username=request.user.username)
    friend = User.objects.get(username=pk)
    if pk == user.username:
        if request.method == 'POST':
            print(request.FILES)
            form = profileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect('profile', request.POST.get('username'))
            else:
                error = 'something went wrong'
                return render(request, 'profile.html',
                              {'user': user, 'form': profileForm(instance=user), 'error': error, 'friend': friend,
                               'user_theme': user.theme})
        else:
            form = profileForm(instance=user)
            return render(request, 'profile.html',
                          {'user': user, 'form': form, 'friend': friend, 'user_theme': user.theme})
    else:
        if request.method == 'POST':
            if 'request' in request.POST:
                Request.objects.create(
                    user1=user.id,
                    user2=friend.id
                )
            elif 'requested' in request.POST:
                for x in Request.objects.all():
                    if x.user1 == user.id and x.user2 == friend.id or x.user1 == friend.id and x.user2 == user.id:
                        x.delete()
            elif 'accept' in request.POST:
                user.friends.add(friend)
                friend.friends.add(user)
                for x in Request.objects.all():
                    if x.user1 == friend.id and x.user2 == user.id:
                        x.delete()
            elif 'reject' in request.POST:
                for x in Request.objects.all():
                    if x.user1 == friend.id and x.user2 == user.id:
                        x.delete()
            else:
                user.friends.remove(friend)
                friend.friends.remove(user)
            return redirect('profile', pk)
        for x in user.friends.all():
            if x.username == pk:
                return render(request, 'profile.html', {'friend': friend, 'is_friend': 3, 'user_theme': user.theme})
        r = Request.objects.all()
        for x in r:
            if x.user1 == user.id and x.user2 == friend.id:
                return render(request, 'profile.html', {'friend': friend, 'is_friend': 2, 'user_theme': user.theme})
            elif x.user1 == friend.id and x.user2 == user.id:
                return render(request, 'profile.html', {'friend': friend, 'is_friend': 1, 'user_theme': user.theme})
        return render(request, 'profile.html', {'friend': friend, 'is_friend': 0, 'user_theme': user.theme})


@login_required(login_url='login_user')
def create_group(request):
    if request.method == 'POST':
        form = groupCreationForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            group.participants.add(request.user)
            return redirect('home')
    else:
        return render(request, 'create-group.html', {'page': 'create', 'form': groupCreationForm(),
                                                     'user_theme': User.objects.get(
                                                         username=request.user.username).theme})


@login_required(login_url='login_user')
def group(request, pk):
    gp = Group.objects.get(id=pk)
    check = False
    for x in gp.participants.all():
        if x.username == request.user.username:
            check = True
            break
    if not check and not gp.is_public:
        return redirect('home')
    error = ''
    if request.method == 'POST' and 'image' in request.POST:
        print(request.POST)
        form = groupCreationForm(request.POST, request.FILES, instance=gp)
        if form.is_valid():
            form.save()
            if 'is_public' in request.POST:
                gp.is_public = True
            else:
                gp.is_public = False
            gp.save()
            return redirect('group', pk)
        else:
            error = 'something went wrong'
    elif request.method == 'POST' and 'leave' in request.POST:
        if gp.owner.username == request.user.username:
            gp.delete()
            return redirect('home')
        else:
            gp.participants.remove(User.objects.get(username=request.user.username))
            return redirect('home')
    members = []
    for x in gp.participants.all():
        members.append({'image': x.image.url, 'username': x.username})
    friends = []
    for x in User.objects.get(id=request.user.id).friends.all():
        check = True
        for y in gp.participants.all():
            if x.id == y.id:
                check = False
                break
        if check:
            friends.append({'image': x.image.url, 'username': x.username, 'click': True})
        else:
            friends.append({'image': x.image.url, 'username': x.username, 'click': False})
    if request.user.username == gp.owner.username:
        return render(request, 'group_owner.html',
                      {'group': gp, 'form': groupCreationForm(instance=gp), 'members': members, 'friends': friends,
                       'error': error, 'user_theme': User.objects.get(username=request.user.username).theme})
    else:
        return render(request, 'group_user.html',
                      {'group': gp, 'form': groupCreationForm(instance=gp), 'members': members, 'friends': friends,
                       'user_theme': User.objects.get(username=request.user.username).theme})


def show(t):
    if t < 10:
        return f"0{t}"
    else:
        return t


def count_time(t):
    time = datetime.datetime.now()
    if time.year > t.year:
        return f"20{show(t.year)}/{show(t.month)}"
    a = datetime.date(time.year, time.month, time.day)
    b = datetime.date(t.year, t.month, t.day)
    days = (a - b).days
    dayofweek = time.weekday()
    if days > 6:
        if t.month == 1:
            return f"Jan {show(t.day)}"
        elif t.month == 2:
            return f"Feb {show(t.day)}"
        elif t.month == 3:
            return f"Mar {show(t.day)}"
        elif t.month == 4:
            return f"Apr {show(t.day)}"
        elif t.month == 5:
            return f"May {show(t.day)}"
        elif t.month == 6:
            return f"Jun {show(t.day)}"
        elif t.month == 7:
            return f"Jul {show(t.day)}"
        elif t.month == 8:
            return f"Aug {show(t.day)}"
        elif t.month == 9:
            return f"Sep {show(t.day)}"
        elif t.month == 10:
            return f"Oct {show(t.day)}"
        elif t.month == 11:
            return f"Nov {show(t.day)}"
        elif t.month == 12:
            return f"Dec {show(t.day)}"
    if days == 0:
        if t.hour < 12:
            return f"{show(t.hour)}:{show(t.minute)} AM"
        else:
            return f"{show(t.hour)}:{show(t.minute)} PM"
    f = (dayofweek - days) % 7
    if f == 0:
        return "mon"
    elif f == 1:
        return "tue"
    elif f == 2:
        return "wed"
    elif f == 3:
        return "thu"
    elif f == 4:
        return "fri"
    elif f == 5:
        return "sat"
    elif f == 6:
        return "sun"


def get_messages(request, pk):
    messages = message.objects.all()
    images = image_message.objects.all()
    response = []
    for m in messages:
        if m.sender.username == pk and m.receiver.username == request.user.username:
            m.seen = "yes"
            m.save(update_fields=['seen'])
        if (m.sender.username == request.user.username and m.receiver.username == pk) or (
                m.sender.username == pk and m.receiver.username == request.user.username):
            if m.updated.hour < 12:
                response.append({'sender': m.sender.username, 'receiver': m.receiver.username, 'text': m.text,
                                 'time': m.created.strftime("%H:%M") + " AM",
                                 'seen': m.seen, 'id': m.id, 'created': m.created, 'type' : 'text'})
            else:
                response.append({'sender': m.sender.username, 'receiver': m.receiver.username, 'text': m.text,
                                 'time': m.created.strftime("%H:%M") + " PM",
                                 'seen': m.seen, 'id': m.id, 'created': m.created, 'type' : 'text'})
    for i in images:
        sender=User.objects.get(id=i.sender)
        receiver=User.objects.get(id=i.receiver)
        if sender.username == pk and receiver.username == request.user.username:
            i.seen = 'yes'
            i.save(update_fields=['seen'])
        if (sender.username == request.user.username and receiver.username == pk) or (
                sender.username == pk and receiver.username == request.user.username):
            if i.updated.hour < 12:
                response.append({'sender': sender.username, 'receiver': receiver.username, 'image': i.image,
                                 'time': i.created.strftime("%H:%M") + " AM",
                                 'seen': i.seen, 'id': i.id, 'created': i.created, 'type' : 'image'})
            else:
                response.append({'sender': sender.username, 'receiver': receiver.username, 'image': i.image,
                                 'time': i.created.strftime("%H:%M") + " PM",
                                 'seen': i.seen, 'id': i.id, 'created': i.created, 'type' : 'image'})

    response.sort(key=lambda x:x['created'])
    return JsonResponse(json.dumps(response, default=str), safe=False)


def get_chats(request):
    messages = message.objects.all()
    images = image_message.objects.all()
    user = User.objects.get(id=request.user.id)
    c = user.id
    u = []
    for m in messages[::-1]:
        if m.sender.id == user.id:
            if m.receiver.id != c:
                if u.count(m.receiver.id) == 0:
                    u.append(m.receiver.id)
                    c = m.receiver.id
        elif m.receiver.id == user.id:
            if m.sender.id != c:
                if u.count(m.sender.id) == 0:
                    u.append(m.sender.id)
                    c = m.sender.id
    for m in images[::-1]:
        if m.sender == user.id:
            if m.receiver != c:
                if u.count(m.receiver) == 0:
                    u.append(m.receiver)
                    c = m.receiver
        elif m.receiver == user.id:
            if m.sender != c:
                if u.count(m.sender) == 0:
                    u.append(m.sender)
                    c = m.sender
    response = []
    for x in u:
        f = User.objects.get(id=x)
        check = False
        for y in user.friends.all():
            if y.id == f.id:
                check = True
                break
        if not check:
            continue
        unseen = 0
        for m in messages:
            if m.sender.id == x and m.receiver.id == user.id and m.seen != 'yes':
                unseen += 1
        for i in images:
            if i.sender == x and i.receiver == user.id and i.seen != 'yes':
                unseen += 1
        last_message=None
        last_image=None
        last=None
        for m in messages[::-1]:
            if m.sender.id == user.id and m.receiver.id == x or m.sender.id == x and m.receiver.id == user.id:
                last_message=m
                break
        for i in images[::-1]:
            if i.sender == user.id and i.receiver == x or i.sender == x and i.receiver == user.id:
                last_image=i
                break

        if not last_image:
            last=last_message
        elif not last_message:
            last=last_image
        else:
            if last_image.created>last_message.created:
                last=last_image
            else:
                last=last_message
        response.append(
            {'type': 'chat', 'image': f.image.url, 'name': f.username, 'id': f.id,
             'time': count_time(last.created), 't': last.created, 'unseen': unseen})

    groups = Group.objects.all()
    group_messages = groupMessage.objects.all()
    group_images = group_image_message.objects.all()
    g = []
    for x in groups[::-1]:
        try:
            if x.participants.all().get(username=request.user.username) is not None:
                g.append(x)
        except:
            pass
    for x in g:
        unseen = 0
        count = 0
        for m in group_messages:
            if m.receiver.id == x.id:
                count += 1
                check = False
                for y in m.seen.all():
                    if y.username == request.user.username:
                        check = True
                        break
                if not check:
                    unseen += 1
        for i in group_images:
            if i.receiver == x.id:
                count += 1
                check = False
                for y in i.seen.all():
                    if y.username == request.user.username:
                        check = True
                        break
                if not check:
                    unseen += 1
        last_message=None
        last_image=None
        last=None
        for m in group_messages[::-1]:
            if m.receiver.id == x.id:
                last_message=m
                break
        for i in group_images[::-1]:
            if i.receiver == x.id:
                last_image=i
                break
        if not last_image:
            last=last_message
        elif not last_message:
            last=last_image
        else:
            if last_image.created>last_message.created:
                last=last_image
            else:
                last=last_message
        if count == 0:
            response.append(
                {'type': 'group', 'name': x.name, 'image': x.image.url, 'id': x.id, 'time': count_time(x.created),
                 't': x.created, 'unseen': unseen})
        else:
            response.append(
                {'type': 'group', 'name': x.name, 'image': x.image.url, 'id': x.id, 'time': count_time(last.updated),
                 't': last.updated, 'unseen': unseen})
    response.sort(key=lambda d: d['t'], reverse=True)
    return JsonResponse(json.dumps(response, default=str), safe=False)


def get_group_messages(request, pk):
    group_messages = groupMessage.objects.all()
    images=group_image_message.objects.all()
    response = []
    for m in group_messages:
        if m.receiver.id == pk:
            check = True
            for x in m.seen.all():
                if x.username == request.user.username:
                    check = False
                    break
            if check:
                m.seen.add(User.objects.get(username=request.user.username))
            message_sender = User.objects.get(username=m.sender.username)
            if m.updated.hour < 12:
                response.append({'sender-username': message_sender.username, 'sender-image': message_sender.image.url,
                                 'text': m.text, 'time': m.created.strftime("%H:%M") + " AM",
                                 'width': len(m.text) * 11 + 88, 'seens': m.seen.count(), 'id': m.id,
                                 'created': m.created, 'type':'text'})
            else:
                response.append({'sender-username': message_sender.username, 'sender-image': message_sender.image.url,
                                 'text': m.text, 'time': m.created.strftime("%H:%M") + " PM",
                                 'width': len(m.text) * 11 + 88, 'seens': m.seen.count(), 'id': m.id,
                                 'created': m.created, 'type':'text'})

    for i in images:
        if i.receiver==pk:
            check=False
            for x in i.seen.all():
                if x.username==request.user.username:
                    check=True
                    break
            if not check:
                i.seen.add(User.objects.get(username=request.user.username))
            image_sender=User.objects.get(id=i.sender)
            if i.updated.hour < 12:
                response.append({'sender-username': image_sender.username, 'sender-image': image_sender.image.url,
                                 'image': i.image, 'time': i.created.strftime("%H:%M") + " AM",
                                  'seens': i.seen.count(), 'id': i.id,
                                 'created': i.created, 'type':'image'})
            else:
                response.append({'sender-username': image_sender.username, 'sender-image': image_sender.image.url,
                                 'image': i.image, 'time': i.created.strftime("%H:%M") + " PM",
                                  'seens': i.seen.count(), 'id': i.id,
                                 'created': i.created, 'type':'image'})

    response.sort(key=lambda x:x['created'])
    return JsonResponse(json.dumps(response, default=str), safe=False)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@csrf_protect
def send_message(request, pk):
    if is_ajax(request) and request.method == "POST":
        message.objects.create(
            sender=request.user,
            receiver=User.objects.get(username=pk),
            text=request.POST.get('message')
        )
        return JsonResponse("success", safe=False)


@csrf_protect
def send_image(request):
    form=imageForm(request.POST,request.FILES)
    if form.is_valid():
        form.save()
        return JsonResponse('yes',safe=False)
    else:
        raise Exception('wrong')


@csrf_protect
def send_group_image(request):
    form=groupImageForm(request.POST,request.FILES)
    if form.is_valid():
        form.save()
        return JsonResponse('yes',safe=False)
    else:
        raise Exception('wrong')


@csrf_protect
def send_group_message(request, pk):
    if is_ajax(request) and request.method == "POST":
        groupMessage.objects.create(
            sender=request.user,
            receiver=Group.objects.get(id=pk),
            text=request.POST.get('message')
        )
        return JsonResponse("success", safe=False)


@csrf_protect
def edit_message(request, pk, text):
    m = message.objects.get(id=pk)
    m.text = text
    m.save()
    return JsonResponse('success', safe=False)


def edit_group_message(request, pk, text):
    m = groupMessage.objects.get(id=pk)
    m.text = text
    m.save()
    return JsonResponse('success', safe=False)


@csrf_protect
def delete_messages(request):
    if is_ajax(request) and request.method == 'POST':
        print(request.POST)
        for x in request.POST['deletes'].split(','):
            if x[0]=='i':
                image_message.objects.get(id=int(x[5:])).image.delete(save=False)
                image_message.objects.get(id=int(x[5:])).delete()
            else:
                message.objects.get(id=int(x)).delete()
    return JsonResponse('yes', safe=False)


def delete_group_messages(request):
    if is_ajax(request) and request.method == 'POST':
        print(request.POST)
        for x in request.POST['deletes'].split(','):
            if x[0]=='i':
                group_image_message.objects.get(id=int(x[5:])).image.delete(save=False)
                group_image_message.objects.get(id=int(x[5:])).delete()
            else:
                groupMessage.objects.get(id=int(x)).delete()
    return JsonResponse('yes', safe=False)


def get_users(request):
    users = User.objects.all()
    response = []
    for x in users:
        response.append({'username': x.username, 'id': x.id, 'image': x.image.url})
    return JsonResponse(json.dumps(response, default=str), safe=False)


def update_status(request):
    s = status.objects.get(user_id=request.user.id)
    s.save()
    return JsonResponse("yes", safe=False)


def get_status(request, pk):
    time = datetime.datetime.now()
    status_time = status.objects.get(user_id=pk).time
    a = datetime.datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)
    b = datetime.datetime(status_time.year, status_time.month, status_time.day, status_time.hour, status_time.minute,
                          status_time.second)
    if ((a - b).total_seconds()) / 60 > 1:
        return JsonResponse(json.dumps(count_time(status.objects.get(user_id=pk).time), default=str), safe=False)
    else:
        return JsonResponse("online", safe=False)


def get_group_status(request, pk):
    gp = Group.objects.get(id=pk)
    c = 0
    o = 0
    for x in gp.participants.all():
        c += 1
        time = datetime.datetime.now()
        status_time = status.objects.get(user_id=User.objects.get(username=x.username).id).time
        a = datetime.datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)
        b = datetime.datetime(status_time.year, status_time.month, status_time.day, status_time.hour,
                              status_time.minute,
                              status_time.second)
        if not (((a - b).total_seconds()) / 60 > 1):
            o += 1
    return JsonResponse(f"{c} members , {o} online", safe=False)


def get_members(request, pk):
    group = Group.objects.get(id=pk)
    print('entered')
    return JsonResponse()


@csrf_protect
def remove_members(request, pk):
    if is_ajax(request) and request.method == "POST":
        gp = Group.objects.get(id=pk)
        for x in request.POST['members'].split(','):
            gp.participants.remove(User.objects.get(username=x))
        return JsonResponse('yes', safe=False)
    else:
        return redirect('group')


@csrf_protect
def add_members(request, pk):
    if is_ajax(request) and request.method == 'POST':
        gp = Group.objects.get(id=pk)
        for x in request.POST['adds'].split(','):
            gp.participants.add(User.objects.get(username=x))
    return JsonResponse('yes', safe=False)


def requests(request):
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        friend = User.objects.get(username=request.POST['username'])
        if 'accept' in request.POST:
            user.friends.add(friend)
            friend.friends.add(user)
            for x in Request.objects.all():
                if x.user1 == friend.id and x.user2 == user.id:
                    x.delete()
        elif 'reject' in request.POST:
            for x in Request.objects.all():
                if x.user1 == friend.id and x.user2 == user.id:
                    x.delete()
    r = []
    for x in Request.objects.all():
        if x.user2 == request.user.id:
            u = User.objects.get(id=x.user1)
            r.append({'username': u.username, 'image': u.image.url, 'id': u.id})
    return render(request, 'requests.html', {'requests': r, 'user_theme': user.theme})


def get_requests(request):
    r = 0
    for x in Request.objects.all():
        if x.user2 == request.user.id:
            r += 1
    return JsonResponse(json.dumps(r), safe=False)


def friends(request):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST" and 'unfriend' in request.POST:
        friend = User.objects.get(username=request.POST.get("username"))
        user.friends.remove(friend)
        return redirect('friends')
    f = []
    for x in user.friends.all():
        f.append({'username': x.username, 'image': x.image.url, 'id': x.id})
    return render(request, 'friends.html', {'friends': f, 'user_theme': user.theme})


def themes(request):
    user_theme = User.objects.get(username=request.user.username).theme
    themes = Theme.objects.all()
    if request.method == 'POST':
        theme = Theme.objects.get(name=request.POST.get('theme'))
        user = User.objects.get(username=request.user.username)
        user.theme = theme
        user.save()
        return redirect('themes')
    return render(request, 'themes.html', {'themes': themes, 'user_theme': user_theme})
