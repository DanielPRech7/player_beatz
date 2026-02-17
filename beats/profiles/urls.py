from django.urls import path

from beats.profiles.views import SignUpView, SignInView, ProfileDetailView, ProfileEditView, signout_view

app_name = 'profiles'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', signout_view, name='signout'),

    path('edit/', ProfileEditView.as_view(), name='edit'),
    path('', ProfileDetailView.as_view(), name='detail'),
]