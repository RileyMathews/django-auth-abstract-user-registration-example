from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from api.models import User
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

class UserRegistrationSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    added_field = serializers.CharField(required=True)

    def get_cleaned_data(self):
        return {
            'added_field': self.validated_data.get('added_field', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])

        # add custom fields
        user.added_field = self.cleaned_data.get('added_field')

        user.save()

        return user