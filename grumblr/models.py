from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="profile")
	# Now that i have related_name i can do User.objects.all()[0].profile.age
	# Code example - from the user object approaching to user profile attribute
	# for user in User.objects.all():
	#	if user.first_name and user.profile.age:
	#		print("Username: " + user.username + " Name: " + user.first_name + " Age: " + str(user.profile.age))
	# Out: Username: fisher Name: Gal Age: 1
	age = models.PositiveIntegerField(blank=True, null=True)
	bio = models.TextField(max_length=420, default="", blank=True)
	profile_pic = models.ImageField(upload_to='profile-pic', blank=True)
	following = models.ManyToManyField("self", related_name="followed")
	is_confirmed = models.BooleanField(default=False)
	# default="" - in django models each field is required by default and is not allowed to be NULL in the database. But I want to initialize bio as empty when a user is created. By setting the default to an empty string, I make it possible to create and save a user profile without specifying bio (and age as well, by null=True) - the bio will be "" when the user is created. <<<==== Make this field allow to be "" when user is created
	# blank= True - this is related to the validation of the ModelForm. After we create a ModelForm from this Model, the form will still consider valid is the user hasn't entered information to the bio field.  <<<==== Make this field allowed to be "" when user updates his information in the form (optional field)

class Message(models.Model):
	user = models.ForeignKey(User) # one (user) to many (messages) relation - every message has a key that is the user it belongs to
	text = models.CharField(max_length=42)
	date = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-date',)

	def get_changes(timestamp=0, stream_type='Home', username_profile=''):
		t = datetime.fromtimestamp(timestamp/1000.0)
		if stream_type == 'Home':
			#messages = Message.objects.filter(date__gt=t).distinct() # remove
			#print('Home:' + str(len(messages))) # remove
			#return messages  # remove
			return Message.objects.filter(date__gt=t).distinct()
		elif stream_type == 'Profile':
			#messages = Message.objects.filter(date__gt=t, user=username_profile).distinct() # remove
			#print('Profile:' + str(len(messages))) # remove
			#return messages # remove
			return Message.objects.filter(date__gt=t, user=username_profile).distinct()
		following = User.objects.get(username=username_profile).profile.following.all()
		#print(username_profile)
		#print(following[0])
		messages = [message for message in Message.objects.filter(date__gt=t).distinct() if message.user.profile in following]
		#for message Message.objects.filter(date__gt=t).distinct() # remove
		#messages = []
		#for message in Message.objects.filter(date__gt=t).distinct():
		#	if message. in User.objects.get(username=request.user).profile.following.all():
		#		messages += Message.objects.filter(user=user)
		#print('following:' + str(len(messages)))# remove
		return messages

class Comment(models.Model):
	message = models.ForeignKey(Message, related_name="comments") # one (message) to many (comments) relation - every message has a key that is the user it belongs to
	user = models.ForeignKey(User, related_name="users") # one (user) to many (comments) relation - every user can have many commnts
	text = models.CharField(max_length=42)
	date = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('date',)
