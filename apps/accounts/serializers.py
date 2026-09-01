from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.organizations.models import Organization

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user account."""
    password = serializers.CharField(write_only=True, min_length=8)
    organization_name = serializers.CharField(
        write_only=True, required=False,
        help_text="If provided, creates a new organization for this user."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'organization_name')

    def create(self, validated_data):
        org_name = validated_data.pop('organization_name', None)
        password = validated_data.pop('password')

        organization = None
        if org_name:
            organization = Organization.objects.create(name=org_name)

        user = User(**validated_data)
        user.set_password(password)
        user.organization = organization
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for reading/updating the current user's profile."""
    organization_name = serializers.CharField(
        source='organization.name', read_only=True
    )
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'organization', 'organization_name',
        )
        read_only_fields = ('id', 'role', 'organization')
