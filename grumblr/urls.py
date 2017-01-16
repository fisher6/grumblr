from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


from django.contrib.auth import views # used for authentication
import grumblr.views

urlpatterns = [
	url(r'^$', grumblr.views.stream, name='home'), # home, index.html
	# Route for built-in authentication with our own custom login page
	url(r'^login$', views.login, {'template_name':'grumblr/login.html'}, name='login'), # built-in authentication using login.html
	url(r'^profile/(?P<username>\w*)$', grumblr.views.profile, name='profile'),
	url(r'^follow-unfollow/(?P<username>\w*)$', grumblr.views.follow_unfollow, name='follow-unfollow'), # HW4
	url(r'^update-profile/$', grumblr.views.update_profile, name='update-profile'), # HW4
	url(r'^change-password/$', grumblr.views.change_password, name='change-password'), # HW4
	url(r'^following/$', grumblr.views.following, name='following'), # home, index.html
	url(r'^logout/$', views.logout_then_login, name='logout'), # logout a user and redirect to login page
	url(r'^register/$', grumblr.views.register, name='register'),
	url(r'^reset_password/$', grumblr.views.reset_password, name='reset-password'),
	url(r'^confirm_email/(?P<username>\w*)$', grumblr.views.confirm_email, name='confirm-email'),
	url(r'^add-post$', grumblr.views.add_post, name='add-post'), # user posts a new message from stream page
	url(r'^get-new-messages$', grumblr.views.get_new_messages, name='get-new-messages'), # for AJAXing new messages
	url(r'^add-post-profile$', grumblr.views.add_post_profile, name='add-post-profile'), # user posts a new message from profile page
	url(r'^add-comment$', grumblr.views.add_comment, name='add-comment'), # user posts a new comment
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
