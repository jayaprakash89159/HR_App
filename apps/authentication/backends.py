"""WorkSphere HR - Custom authentication backend (email-based login)"""
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailAuthBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None
        try:
            user = UserModel.objects.get(email=username.lower())
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
