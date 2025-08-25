from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp
import qrcode
import base64
from io import BytesIO

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'Owner')  # Default to Owner if not provided

    if not username or not password or not email:
        return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password, role=role)
    return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    token = request.data.get('token')

    user = authenticate(username=username, password=password)

    if user is not None:
        # Check if 2FA is enabled
        if user.two_factor_secret:
            totp = pyotp.TOTP(user.two_factor_secret)
            if not totp.verify(token):
                return Response({'error': 'Invalid 2FA token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'two_factor_enabled': bool(user.two_factor_secret),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_2fa(request):
    user = request.user

    # If 2FA already exists, return existing QR
    if user.two_factor_secret:
        secret = user.two_factor_secret
    else:
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        user.save()

    totp = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(name=user.email, issuer_name="Pretium Investment")

    # Create QR Code
    img = qrcode.make(otp_uri)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    return Response({
        'otp_uri': otp_uri,
        'qr_code_base64': img_base64
    })