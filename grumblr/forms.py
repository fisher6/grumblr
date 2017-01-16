from django import forms

from django.contrib.auth.models import User
from grumblr.models import * # import my grumblr models

class AddPostForm(forms.Form):
	text = forms.CharField(max_length=42, widget=forms.Textarea({'cols': 23, 'rows': 3, 'placeholder': "  What's on your mind?"}))

	def clean_username(self):
		username_clean = self.cleaned_data.get('username')
		if User.objects.filter(username=username_clean): # if list isn't empty it evaluates to True and it means username already exists
			raise forms.ValidationError("Username already exists")
		return username_clean

class AddCommentForm(forms.Form):
	text = forms.CharField(max_length=42, widget=forms.Textarea({'cols': 23, 'rows': 3, 'placeholder': "  What's on your mind?"}))

	def clean_username(self):
		username_clean = self.cleaned_data.get('username')
		if User.objects.filter(username=username_clean): # if list isn't empty it evaluates to True and it means username already exists
			raise forms.ValidationError("Username already exists")
		return username_clean

class RegisterForm(forms.Form):
	first_name = forms.CharField(max_length = 20) # label='First Name' not needed, Django Forms does it automatically from first_name
	last_name = forms.CharField(max_length = 20)
	email = forms.EmailField(max_length = 50)
	username = forms.CharField(max_length = 30)
	password = forms.CharField(max_length = 100, widget=forms.PasswordInput()) # the input type will be password.
	confirm_password = forms.CharField(max_length = 100, widget=forms.PasswordInput())
	# the idea of the widget=forms.Pass.. is that the field widget controls how the field is displayed on the page - the user interface. <<<<=== widget - controls the user interface aspect of the form.


	# clean(self) - VALIDATES THE WHOLE FORM (good for validation of two values of forms together like password and confirm password)
	# clean_<fieldname> - VALIDATES A SPECIFIC FORM FIELD

	# How the form should be validated. By default the Forms.form class - the parent of our registration form class - defines a clean function that implements default validation code for the form. It checks if all the required fields are present and contain data of the appropriate type (integer field has a number and so on)
	# By default - all fields of a form are required unless they are marked as required='false' in the field constructor above.
	# Here we are overriding our parent's clean function to provide our own validation function
	def clean(self):
		# First thing to do always in form validation function - call the default validation function.
		# Calls our parent (forms.Form) .clean function, gets a dictionary of cleaned data as a result - only the form field that met the requirements of the field type (if integer didn't feel an integer - it won't be in a dictionary). The cleaned data is already converted to Python datatype
		cleaned_data = super(RegisterForm, self).clean() # super takes a class, and a instance of the class and return a instance of the parent class
		# Confirms that the two password fields match - that's the only thing we need to do that the default validation function of forms.Form didn't do
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')
		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError("Failed to confirm password", code='confirmed password') # report error in form in Django - throwing exception to Django built in code that calls the clean function - it will catch the exception and outputs the error for u
		#return the cleaned data we got from our parent.
		return cleaned_data

	# Customizes form validation for the username field. - adding custom validation function for individual field by name clean_<fieldname>
	# This functions (field specific validation functions) are called before (?) the the clean() function which validates the whole form - so we can access the cleaned_data from self.
	def clean_username(self):
		username_clean = self.cleaned_data.get('username')
		if User.objects.filter(username=username_clean): # if list isn't empty it evaluates to True and it means username already exists
			raise forms.ValidationError("Username %(username)s already exists", params={'username': username_clean}, code='used username') # Provide a descriptive error code to the ValidationError constructor under "code"
		return username_clean

class ResetPasswordForm(forms.Form):
	username = forms.CharField(max_length = 30)
	email = forms.EmailField(max_length = 50)

	def clean_username(self):
		username_clean = self.cleaned_data.get('username')
		if not User.objects.filter(username=username_clean):
			raise forms.ValidationError("Username %(username)s doesn't exist", params={'username': username_clean}, code='not existent username')
		return username_clean

	def clean_email(self):
		username_clean = self.cleaned_data.get('username')
		email_clean = self.cleaned_data.get('email')
		if User.objects.get(username=username_clean).email != email_clean:
			raise forms.ValidationError("Email doesn't match the email you registered with", code='bad email')
		return email_clean

class UserForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'True'})) # can't change username - design decision
	#email = forms.EmailField() # Change email not required in specification for HW4

	class Meta:
		model = User
		fields = ["username", "first_name", "last_name"] # ,"email]

class UserProfileForm(forms.ModelForm):
	bio = forms.CharField(widget=forms.Textarea({'cols': 23, 'rows': 6, 'placeholder': "Tell us about yourself..."}), required=False)
	class Meta:
		model = UserProfile
		fields = ["age", "bio", "profile_pic"]
		widgets = {'profile_pic': forms.FileInput()} # override the default widget for picture, cause the default behavior let a user remove a picture
