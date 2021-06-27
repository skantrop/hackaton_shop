from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This User is already registered!")
        return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match!')
        return attrs

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.create_activation_code()
        User.send_activation_mail(user.email, user.activation_code)
        return user


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    activation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        activation_code = attrs.get('activation_code')
        if not User.objects.filter(email=email, activation_code=activation_code).exists():
            raise serializers.ValidationError('User is not found')
        return attrs

    def activate(self):
        data = self.validated_data
        user = User.objects.get(**data)
        user.is_active = True
        user.activation_code = ''
        user.save()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password, request=self.context.get('request'))
            if not user:
                raise serializers.ValidationError('Written Username and Password seems to be incorrect')
        else:
            raise serializers.ValidationError('Email and password are required!')
        attrs['user'] = user
        return attrs


class RestorePasswordSerializer(serializers.Serializer):
    pass


class ChangePasswordSerializer(serializers.Serializer):
    pass
