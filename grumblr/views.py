from django.shortcuts import render, redirect, get_object_or_404 #404 - HW4
from django.core.urlresolvers import reverse #HW4
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import random # password generator

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Used to send email in Django - HW4
from django.core.mail import send_mail

# Used to change password - HW4
from django.contrib.auth.forms import SetPasswordForm # can also use PasswordChangeForm - ask to enter old password too

from grumblr.models import *
from grumblr.forms import *

import time # HW5
current_milli_time = lambda: int(round(time.time() * 1000)) #HW5

@login_required
def stream(request):
	if not request.user or not User.objects.filter(username=request.user): # GET request validation, if logged-in user maliciously tries to change the GET values of the request, entering a username who doesn't exist in the request.user or an empty string username - the get request for the first name will throw an error. Might not needed for this HW, cause it's not a validation of POST request information, but just to make sure.
		context = {'errors': ["Invalid request."], 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context) # can also use Http404("Invalid Request") (from django.http import Http404)
	context = {'messages': Message.objects.all, 'username': request.user.username ,'first_name': User.objects.get(username=request.user).first_name, 'user_profile': get_object_or_404(UserProfile, user=request.user), 'form': AddPostForm(), 'timestamp': current_milli_time()}
	return render(request, 'grumblr/index.html', context)

@login_required
def following(request):
	if not request.user or not User.objects.filter(username=request.user): # GET request validation, if logged-in user maliciously tries to change the GET values of the request, entering a username who doesn't exist in the request.user or an empty string username - the get request for the first name will throw an error. Might not needed for this HW, cause it's not a validation of POST request information, but just to make sure.
		context = {'errors': ["Invalid request."], 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context) # can also use Http404("Invalid Request") (from django.http import Http404)
	messages = []
	following = User.objects.get(username=request.user).profile.following.all()
	for user in User.objects.all():
		if user.profile in following:
			messages += Message.objects.filter(user=user)
	context = {'messages': sorted(messages, key=lambda x: x.date, reverse=True), 'username': request.user.username,'first_name': User.objects.get(username=request.user).first_name, 'user_profile': get_object_or_404(UserProfile, user=request.user), 'timestamp': current_milli_time()}
	return render(request, 'grumblr/following.html', context)

@login_required
def profile(request, username):
	try:
		user_object = User.objects.get(username=username) # When populating your context, don't make multiple queries to the database cause that is quite inefficient. Store the query result as a variable and access the variable.
		context = {'messages': Message.objects.filter(user=user_object), 'username': username, 'first_name': user_object.first_name, 'last_name': user_object.last_name, 'user_profile': user_object.profile, 'following': user_object.profile in User.objects.get(username=request.user).profile.following.all(), 'form': AddPostForm(), 'timestamp': current_milli_time()} # to show user's information in his profile page
		return render(request, 'grumblr/profile.html', context)
	except ObjectDoesNotExist:
		context = {'messages': Message.objects.all, 'username': request.user.username, 'first_name': User.objects.get(username=request.user).first_name, 'errors': ["User " + username + " does not exist."], 'form': AddPostForm(), 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context)

@login_required
def follow_unfollow(request, username):
	if username == request.user.username: # user can't follow himself
		user_object = User.objects.get(username=username)
		context = {'messages': Message.objects.filter(user=user_object), 'username': username, 'first_name': user_object.first_name, 'last_name': user_object.last_name, 'user_profile': user_object.profile, 'form': AddPostForm(), 'errors': ["You can't follow yourself."], 'timestamp': current_milli_time()} # to show user's information in his profile page
		return render(request, 'grumblr/profile.html', context)
	try:
		user_object = User.objects.get(username=username) # When populating your context, don't make multiple queries to the database cause that is quite inefficient. Store the query result as a variable and access the variable.
		me_object = User.objects.get(username=request.user)
		if user_object.profile in me_object.profile.following.all(): # already following, unfollow
			me_object.profile.following.remove(user_object.profile)
			following = False
		else: # follow
			me_object.profile.following.add(user_object.profile)
			following = True
		me_object.profile.save()
		context = {'messages': Message.objects.filter(user=user_object), 'username': username, 'first_name': user_object.first_name, 'last_name': user_object.last_name, 'user_profile': user_object.profile, 'following': following, 'form': AddPostForm(), 'timestamp': current_milli_time()} # to show user's information in his profile page
		return render(request, 'grumblr/profile.html', context)
	except ObjectDoesNotExist:
		context = {'messages': Message.objects.all, 'username': request.user.username, 'first_name': User.objects.get(username=request.user).first_name, 'errors': ["User " + username + " does not exist."], 'form': AddPostForm(), 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context)

@login_required
def add_post(request):
	if not request.user or not User.objects.filter(username=request.user): # GET request validation, if logged-in user maliciously tries to change the GET values of the request, entering a username who doesn't exist in the request.user or an empty string username - the get request for the first name will throw an error. Might not needed for this HW, cause it's not a validation of POST request information, but just to make sure.
		context = {'errors': ["Invalid request"], 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context)
	try:
		timestamp = float(request.POST['timestamp'])
	except:
		timestamp = 0.0
	messages = Message.objects.all()
	context = {'messages': messages, 'username': request.user.username, 'first_name': User.objects.get(username=request.user).first_name, 'user_profile': get_object_or_404(UserProfile, user=request.user), 'timestamp': current_milli_time()}
	if request.method == 'GET': # request is a GET
		context['form'] = AddPostForm()
		return render(request, 'grumblr/index.html', context)
	# POST only saves the message, we don't use the returned information to update
	# the messages - it is done in get_new_messages using updateChanges() JS function
	#messages = Message.get_changes(timestamp)
	#context['messages'] = messages
	form = AddPostForm(request.POST) # request is a POST
	#context['form'] = form
	if not form.is_valid():
		return render(request, 'grumblr/messages.json', context, content_type='application/json')
	new_message = Message(user=request.user,text=form.cleaned_data['text']) # request.user is correct, checked in the if at the start of the function
	new_message.save()
	return render(request, 'grumblr/messages.json', context, content_type='application/json')

@login_required
def add_comment(request):
	if not request.user or not User.objects.filter(username=request.user): # GET request validation, if logged-in user maliciously tries to change the GET values of the request, entering a username who doesn't exist in the request.user or an empty string username - the get request for the first name will throw an error. Might not needed for this HW, cause it's not a validation of POST request information, but just to make sure.
		context = {'errors': ["Invalid request"], 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context)
	messages = Message.objects.all()
	context = {'messages': messages, 'username': request.user.username, 'first_name': User.objects.get(username=request.user).first_name, 'user_profile': get_object_or_404(UserProfile, user=request.user), 'timestamp': current_milli_time()}
	if request.method == 'GET': # request is a GET
		context['form'] = AddPostForm()
		context['errors'] = ["Wrong request!"]
		return render(request, 'grumblr/index.html', context)
	new_comment = Comment(message=Message.objects.get(id=request.POST['message_id']), user=User.objects.get(username=request.user),text=request.POST['text']) # request.user is correct, checked in the if at the start of the function
	new_comment.save()
	context = {'comment': new_comment}
	return render(request, 'grumblr/comment.json', context, content_type='application/json')

@login_required
def get_new_messages(request):
	if not request.user or not User.objects.filter(username=request.user) or not 'stream_type' in request.GET \
	or (request.GET['stream_type'] != 'Home' and request.GET['stream_type'] != 'Profile' and request.GET['stream_type'] != 'Following'):
	# GET request validation, if logged-in user maliciously tries to change the GET values of the request, entering a username who doesn't exist in the request.user or an empty string username - the get request for the first name will throw an error. Might not needed for this HW, cause it's not a validation of POST request information, but just to make sure.
		context = {'errors': ["Invalid request"], 'timestamp': current_milli_time()}
		return render(request, 'grumblr/messages.json', context, content_type='application/json')
	username_profile = ""
	if request.GET['stream_type'] == 'Profile':
		try:
			username_profile = User.objects.get(username=request.GET['username_profile'])
		except:
			context = {'errors': ["Invalid request"], 'timestamp': current_milli_time()}
			return render(request, 'grumblr/messages.json', context, content_type='application/json')
	if request.GET['stream_type'] == 'Following':
		username_profile = request.user
	try:
		timestamp = float(request.GET['timestamp'])
	except:
		timestamp = 0.0
	context = {'messages': Message.get_changes(timestamp, request.GET['stream_type'], username_profile), 'username': request.user.username, 'first_name': User.objects.get(username=request.user).first_name, 'user_profile': get_object_or_404(UserProfile, user=request.user), 'form': AddPostForm(), 'timestamp': current_milli_time()}
	return render(request, 'grumblr/messages.json', context, content_type='application/json')

@login_required
def add_post_profile(request):
	if not request.user or not User.objects.filter(username=request.user): # GET request validation, if logged-in user maliciously tries to change the GET values of the request, entering a username who doesn't exist in the request.user or an empty string username - the get request for the first name will throw an error. Might not needed for this HW, cause it's not a validation of POST request information, but just to make sure.
		context = {'errors': ["Invalid request"], 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context)
	user_object = User.objects.get(username=request.user)
	context = {'messages': Message.objects.filter(user=request.user), 'username': request.user.username, 'first_name': user_object.first_name, 'last_name': user_object.last_name, 'user_profile': get_object_or_404(UserProfile, user=request.user), 'form': AddPostForm(), 'timestamp': current_milli_time()} # to show logged in user's information in his profile page
	if request.method == 'GET': # request is a POST
		context['form'] = AddPostForm()
		return render(request, 'grumblr/profile.html', context)
	form = AddPostForm(request.POST)
	context['form'] = form
	if not form.is_valid():
		return render(request, 'grumblr/profile.html', context)
	new_message = Message(user=request.user,text=form.cleaned_data['text'])
	new_message.save()
	return render(request, 'grumblr/profile.html', context)

@transaction.atomic # this run after username validation, if it won't be atomic there is a chance for race condition if different process creates user with the same username
def register(request):
	context = {}
	if request.method == 'GET': # case where the user just wants to register, not submit the registration form, and gets redirected to register.html
		if request.user.username: # if user's already logged in, redirect to home page
			return redirect('/')
		context['form'] = RegisterForm()
		return render(request, 'grumblr/register.html', context)
	# input validation check
	form = RegisterForm(request.POST)
	context['form'] = form
	if not form.is_valid():
		return render(request, 'grumblr/register.html', context)
	# Creating user - input validated and transaction is atomic so no need for error handerlin
	new_user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'], email=form.cleaned_data['email'], first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'])
	new_user.save()
	new_user_profile = UserProfile(user=new_user) # need to create UserProfile instance to the newly created User
	new_user_profile.profile_pic = '/profile-pic/profile.png'
	new_user_profile.save()
	# New user created - authenticate him and redicted to login page
	new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
	login(request, new_user)
	# send email
	email_body = """
	Welcome to Grumblr, %s!
	Please confirm your email by clicking here: http://%s%s
	""" % (request.user.username, request.get_host(), "/confirm_email/" + new_user.username) # change new_user
	send_mail(subject="Welcome to Grumblr!", message=email_body, from_email="admin@grumblr.com", recipient_list=[new_user.email]) # change new_user
	context['email'] = form.cleaned_data['email']
	#return redirect('/')
	return render(request, 'grumblr/confirmation_page.html', context)

def reset_password(request):
	context = {}
	if request.method == 'GET':
		if request.user.username: # if user's already logged in, redirect to home page
			return redirect('/')
		context['form'] = ResetPasswordForm()
		return render(request, 'grumblr/reset_password.html', context)
	# input validation check
	form = ResetPasswordForm(request.POST)
	context['form'] = form
	if not form.is_valid():
		return render(request, 'grumblr/reset_password.html', context)
	password_chars = "abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
	password = ''.join([password_chars[random.randrange(len(password_chars))] for x in list(range(8))]) # 8 chars password
	user = User.objects.get(username=form.cleaned_data['username'])
	user.set_password = password
	user.save()
	email_body = """
	Grumblr password recovery for %s \nYour new password is %s - don't lose it !
	""" % (form.cleaned_data['username'], password)
	send_mail(subject="Grumblr - Password Reset", message=email_body, from_email="admin@grumblr.com", recipient_list=[form.cleaned_data['email']])
	return redirect('/')


@login_required
def confirm_email(request, username):
	context = {}
	if len(User.objects.filter(username=username)) == 0:
		errors = ["Invalid username."]
		context = {'messages': Message.objects.all, 'username': request.user.username, 'form': AddPostForm(), 'errors': errors, 'timestamp': current_milli_time()}
		return render(request, 'grumblr/index.html', context)
	user_object = get_object_or_404(User, username=username)
	if user_object.username != request.user.username:
		errors = ["You can't confirm someone else's email"]
	elif user_object.profile.is_confirmed:
		errors = ["You already confirmed your email!"]
	else:
		user_object.profile.is_confirmed = True
		user_object.profile.save()
		errors = ["Email confirmed!"]
	context = {'messages': Message.objects.all, 'username': request.user.username, 'first_name': user_object.first_name, 'form': AddPostForm(), 'errors': errors, 'timestamp': current_milli_time()}
	return render(request, 'grumblr/index.html', context)

@login_required
def update_profile(request):
	user = get_object_or_404(User, username=request.user) # just like User.objects.get(username=request.user), if get fails (none found or more than one found) return 404
	user_profile = get_object_or_404(UserProfile, user=request.user)
	if request.method == 'GET':
		return render(request, 'grumblr/update_profile.html', {'user_form': UserForm(instance=user), 'user_profile_form': UserProfileForm(instance=user_profile), 'timestamp': current_milli_time()}) # create UserForm with instance=user so the user can see his profile information already populate and edit them
	# POST request
	user_form = UserForm(request.POST, instance=user) # we take the UserForm that belongs to user - which is the User instance of the logged in user (request.user), and fill it with the information from the post request - the input. So any input of the user will overwrite what is now in UserForm(instance=user) - the user's form before pressing "update profile"
	user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile) # request.FILES for the profile image
	set_password_form = SetPasswordForm(data=request.POST, user=user) # request.FILES for the profile image
	if not user_form.is_valid() or not user_profile_form.is_valid():
		return render(request, 'grumblr/update_profile.html', {'user_form': UserForm(instance=user), 'user_profile_form': UserProfileForm(instance=user_profile), 'timestamp': current_milli_time()})
	user_form.save()
	user_profile_form.save()
	user_object = User.objects.get(username=request.user) # saving multiple DB queries at next command for first/last name
	context = {'messages': Message.objects.filter(user=request.user), 'username': request.user.username, 'first_name': user_object.first_name, 'last_name': user_object.last_name, 'user_profile': user_profile, 'form': AddPostForm(), 'timestamp': current_milli_time()}
	return redirect(reverse('profile', args=[request.user.username])) # Django reverse URL resolver (urls.py), with parameter


@login_required
def change_password(request):
	user = get_object_or_404(User, username=request.user) # just like User.objects.get(username=request.user), if get fails (none found or more than one found) return 404
	if request.method == 'GET':
		return render(request, 'grumblr/change_password.html', {'set_password_form': SetPasswordForm(user=user), 'timestamp': current_milli_time()})
	# POST request
	set_password_form = SetPasswordForm(data=request.POST, user=user) # request.FILES for the profile image
	if not set_password_form.is_valid():
		return render(request, 'grumblr/change_password.html', {'set_password_form': SetPasswordForm(user=user), 'password_error': set_password_form.errors, 'timestamp': current_milli_time()})
	set_password_form.save()
	user_object = User.objects.get(username=request.user) # saving multiple DB queries at next command for first/last name
	user_profile = get_object_or_404(UserProfile, user=request.user) # same ^^^^
	context = {'messages': Message.objects.filter(user=request.user), 'username': request.user.username, 'first_name': user_object.first_name, 'last_name': user_object.last_name, 'user_profile': user_profile, 'form': AddPostForm(), 'timestamp': current_milli_time()}
	return redirect(reverse('profile', args=[request.user.username])) # Django reverse URL resolver (urls.py), with parameter
