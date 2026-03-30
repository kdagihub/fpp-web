from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from apps.accounts.models import User
from apps.members.models import MemberProfile


class RegisterSerializer(serializers.Serializer):
    """Inscription — crée un User + MemberProfile."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    sex = serializers.ChoiceField(choices=MemberProfile.SexChoices.choices)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    city = serializers.CharField(max_length=100)
    commune = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    profession = serializers.CharField(max_length=100, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100, required=False, allow_blank=True)
    motivation = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value.lower()

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Un compte avec ce numéro existe déjà.")
        return value or None

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        password_validation.validate_password(data["password"])
        return data

    def create(self, validated_data):
        profile_fields = {
            "sex": validated_data.pop("sex"),
            "date_of_birth": validated_data.pop("date_of_birth", None),
            "city": validated_data.pop("city"),
            "commune": validated_data.pop("commune"),
            "region": validated_data.pop("region", ""),
            "profession": validated_data.pop("profession", ""),
            "neighborhood": validated_data.pop("neighborhood", ""),
            "motivation": validated_data.pop("motivation", ""),
        }
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data.get("phone"),
        )

        MemberProfile.objects.create(user=user, **profile_fields)
        return user


class LoginSerializer(serializers.Serializer):
    """Connexion — email + mot de passe."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"].lower(), password=data["password"])
        if user is None:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")
        if not user.is_active:
            raise serializers.ValidationError("Ce compte a été désactivé.")
        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Profil de l'utilisateur connecté (GET /api/auth/me/)."""

    matricule = serializers.CharField(source="member_profile.matricule", read_only=True)
    sex = serializers.CharField(source="member_profile.sex", read_only=True)
    date_of_birth = serializers.DateField(source="member_profile.date_of_birth", read_only=True)
    city = serializers.CharField(source="member_profile.city", read_only=True)
    commune = serializers.CharField(source="member_profile.commune", read_only=True)
    region = serializers.CharField(source="member_profile.region", read_only=True)
    neighborhood = serializers.CharField(source="member_profile.neighborhood", read_only=True)
    profession = serializers.CharField(source="member_profile.profession", read_only=True)
    membership_status = serializers.CharField(source="member_profile.membership_status", read_only=True)
    membership_date = serializers.DateTimeField(source="member_profile.membership_date", read_only=True)

    active_roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "phone", "first_name", "last_name", "avatar",
            "is_staff", "is_active", "created_at",
            "matricule", "sex", "date_of_birth", "city", "commune",
            "region", "neighborhood", "profession",
            "membership_status", "membership_date",
            "active_roles",
        ]
        read_only_fields = ["id", "email", "is_staff", "is_active", "created_at"]

    def get_active_roles(self, obj):
        roles = obj.party_roles.filter(is_active=True).select_related("role", "zone")
        return [
            {
                "role_id": str(ur.role.id),
                "role_name": ur.role.name,
                "role_level": ur.role.level,
                "zone_name": ur.zone.name if ur.zone else None,
                "assigned_at": ur.created_at.isoformat() if ur.created_at else None,
            }
            for ur in roles
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Modification du profil (PATCH /api/auth/me/)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Ce numéro est déjà utilisé.")
        return value or None


class PasswordChangeSerializer(serializers.Serializer):
    """Changement de mot de passe (utilisateur connecté)."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Les mots de passe ne correspondent pas."})
        password_validation.validate_password(data["new_password"], self.context["request"].user)
        return data


class PasswordResetSerializer(serializers.Serializer):
    """Demande de reset de mot de passe — envoie un email."""

    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower()

    def get_reset_data(self):
        email = self.validated_data["email"]
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return None
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        token = default_token_generator.make_token(user)
        return {"user": user, "uid": uid, "token": token}


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirmation du reset avec uid + token."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Les mots de passe ne correspondent pas."})

        try:
            uid = urlsafe_base64_decode(data["uid"]).decode()
            user = User.objects.get(pk=uid)
        except (ValueError, TypeError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Lien invalide."})

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError({"token": "Le lien a expiré ou est invalide."})

        password_validation.validate_password(data["new_password"], user)
        data["user"] = user
        return data
