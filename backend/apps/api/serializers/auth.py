import datetime
import re

from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.models import Permission
from rest_framework import serializers

PHONE_RE = re.compile(r"^\+?[\d\s\-]{8,20}$")

from apps.accounts.models import User


class RegisterSerializer(serializers.Serializer):
    """Phase 1 — inscription sympathisant (User seul, pas de MemberProfile)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    sex = serializers.ChoiceField(choices=User.SexChoices.choices)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    date_of_birth = serializers.DateField()
    cgu_accepted = serializers.BooleanField()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value.lower()

    def validate_phone(self, value):
        if not value:
            return None
        cleaned = re.sub(r"[\s\-]", "", value)
        if not PHONE_RE.match(value) or len(cleaned.lstrip("+")) < 8:
            raise serializers.ValidationError(
                "Numéro invalide. Utilisez uniquement des chiffres (ex: +225 0701020304)."
            )
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Un compte avec ce numéro existe déjà.")
        return value

    def validate_date_of_birth(self, value):
        today = datetime.date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("Vous devez avoir au moins 18 ans pour vous inscrire.")
        return value

    def validate(self, data):
        if not data.get("cgu_accepted"):
            raise serializers.ValidationError(
                {"cgu_accepted": "Vous devez accepter les CGU et la Politique de confidentialité."}
            )
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        password_validation.validate_password(data["password"])
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data.pop("cgu_accepted")
        now = timezone.now()
        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                sex=validated_data["sex"],
                phone=validated_data.get("phone"),
                date_of_birth=validated_data["date_of_birth"],
                cgu_accepted_at=now,
                privacy_accepted_at=now,
            )
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
        if not user.email_verified:
            raise serializers.ValidationError(
                "Votre email n'est pas encore vérifié. "
                "Consultez votre boîte de réception ou demandez un nouvel email de vérification."
            )
        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Profil complet — gère le cas où member_profile n'existe pas (sympathisant)."""

    membership = serializers.SerializerMethodField()
    active_roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "email_verified", "phone", "first_name", "last_name", "sex",
            "date_of_birth", "avatar", "is_staff", "is_superuser", "is_active",
            "is_emergency_user", "created_at", "membership", "active_roles", "permissions",
        ]
        read_only_fields = [
            "id", "email", "email_verified", "is_staff", "is_superuser", "is_active",
            "is_emergency_user", "created_at",
        ]

    def get_membership(self, obj):
        profile = getattr(obj, "member_profile", None)
        if profile is None:
            return None
        photo_url = None
        if profile.photo:
            request = self.context.get("request")
            photo_url = request.build_absolute_uri(profile.photo.url) if request else profile.photo.url
        return {
            "matricule": profile.matricule,
            "status": profile.membership_status,
            "id_document_type": profile.id_document_type,
            "id_document_number": profile.id_document_number,
            "city": profile.city,
            "commune": profile.commune,
            "region": profile.region,
            "neighborhood": profile.neighborhood,
            "profession": profile.profession,
            "photo": photo_url,
            "membership_validated_at": profile.membership_date.isoformat() if profile.membership_date else None,
            "membership_requested_at": profile.created_at.isoformat() if profile.created_at else None,
        }

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

    def get_permissions(self, obj):
        if obj.is_superuser:
            return ["*"]
        user_perms = obj.user_permissions.all()
        group_perms = Permission.objects.filter(group__user=obj)
        return sorted({p.codename for p in (user_perms | group_perms)})


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Modification du profil (PATCH /api/auth/me/)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]

    def validate_phone(self, value):
        if not value:
            return None
        if not PHONE_RE.match(value):
            raise serializers.ValidationError(
                "Numéro invalide. Utilisez uniquement des chiffres (ex: +225 0701020304)."
            )
        if User.objects.filter(phone=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Ce numéro est déjà utilisé.")
        return value


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
