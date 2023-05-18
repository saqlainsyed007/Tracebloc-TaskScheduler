import json

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["POST"])
def login(request):
    try:
        request_data = json.loads(request.body)
    except Exception:
        err_data = {"error": "Invalid request data. Request body must be a JSON with username/email and password"}
        return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)

    username = request_data.get("username")
    email = request_data.get("email")

    if not username and not email:
        err_data = {"error": "Either username or email must be provided"}
        return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)

    user_filter_param = {"username": username} if username else {"email": email}

    User = get_user_model()
    user = User.objects.filter(**user_filter_param).first()
    if not user:
        err_data = {
            "error": f"User not found with {user_filter_param}"
        }
        return Response(status=status.HTTP_401_UNAUTHORIZED, data=err_data)

    password = request_data.get("password", "")
    if not password:
        err_data = {"error": "Password must be provided"}
        return Response(status=status.HTTP_400_BAD_REQUEST, data=err_data)
    if not user.is_active or not user.check_password(password):
        err_data = {"error": "Invalid Credentials"}
        return Response(status=status.HTTP_401_UNAUTHORIZED, data=err_data)

    token = Token.objects.get_or_create(user=user)[0].key
    return Response(data={"token": token})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response('User Logged out successfully')
