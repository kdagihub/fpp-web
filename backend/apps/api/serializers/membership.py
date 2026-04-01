from django.db import transaction
from rest_framework import serializers

from apps.members.models import MemberProfile

MAX_UPLOAD_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")


def validate_image_file(file_obj, field_label="Fichier"):
    """Validation senior : taille max et types MIME autorisés."""
    if file_obj.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise serializers.ValidationError(
            f"{field_label} : taille maximale {MAX_UPLOAD_SIZE_MB} Mo dépassée."
        )
    if hasattr(file_obj, "content_type") and file_obj.content_type not in ALLOWED_IMAGE_TYPES:
        types = ", ".join(ALLOWED_IMAGE_TYPES)
        raise serializers.ValidationError(
            f"{field_label} : format non supporté. Formats acceptés : {types}."
        )
    return file_obj


class MembershipRequestSerializer(serializers.Serializer):
    """Phase 2 — demande d'adhésion. Crée le MemberProfile (status=pending)."""

    id_document_type = serializers.ChoiceField(choices=MemberProfile.IdDocumentType.choices)
    id_document_number = serializers.CharField(max_length=30)
    id_document_scan = serializers.ImageField()
    photo = serializers.ImageField()
    city = serializers.CharField(max_length=100)
    commune = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    profession = serializers.CharField(max_length=100, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True, max_length=500)
    motivation = serializers.CharField(required=False, allow_blank=True, max_length=2000)

    def validate_id_document_number(self, value):
        if MemberProfile.objects.filter(id_document_number=value).exists():
            raise serializers.ValidationError("Ce numéro de pièce d'identité est déjà utilisé.")
        return value

    def validate_id_document_scan(self, value):
        return validate_image_file(value, "Scan de la pièce d'identité")

    def validate_photo(self, value):
        return validate_image_file(value, "Photo de profil")

    def validate(self, data):
        user = self.context["request"].user
        try:
            user.member_profile
            raise serializers.ValidationError(
                {"detail": "Vous avez déjà soumis une demande d'adhésion."}
            )
        except MemberProfile.DoesNotExist:
            pass
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        ua = self.context["request"].META.get("HTTP_USER_AGENT", "").lower()
        source = "mobile" if "mobile" in ua else "web"

        with transaction.atomic():
            profile = MemberProfile.objects.create(
                user=user,
                id_document_type=validated_data["id_document_type"],
                id_document_number=validated_data["id_document_number"],
                id_document_scan=validated_data["id_document_scan"],
                photo=validated_data["photo"],
                city=validated_data["city"],
                commune=validated_data["commune"],
                region=validated_data.get("region", ""),
                profession=validated_data.get("profession", ""),
                neighborhood=validated_data.get("neighborhood", ""),
                address=validated_data.get("address", ""),
                motivation=validated_data.get("motivation", ""),
                registration_source=source,
            )
        return profile


class MembershipDetailSerializer(serializers.ModelSerializer):
    """Détail du profil membre pour le user connecté."""

    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_sex = serializers.CharField(source="user.sex", read_only=True)
    user_date_of_birth = serializers.DateField(source="user.date_of_birth", read_only=True)
    registered_at = serializers.DateTimeField(source="user.created_at", read_only=True)
    membership_requested_at = serializers.DateTimeField(source="created_at", read_only=True)
    membership_validated_at = serializers.DateTimeField(source="membership_date", read_only=True)

    class Meta:
        model = MemberProfile
        fields = [
            "id", "user_full_name", "user_email", "user_sex", "user_date_of_birth",
            "matricule", "id_document_type", "id_document_number",
            "city", "commune", "region", "neighborhood",
            "profession", "motivation",
            "membership_status",
            "registered_at", "membership_requested_at", "membership_validated_at",
            "registration_source",
        ]
        read_only_fields = fields


class VerifyMatriculeSerializer(serializers.Serializer):
    """Input pour la vérification admin d'un matricule."""

    matricule = serializers.CharField(max_length=30)


class VerifyMatriculeResultSerializer(serializers.ModelSerializer):
    """Output complet pour la vérification admin — toutes les infos du membre."""

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone")
    sex = serializers.CharField(source="user.sex")
    date_of_birth = serializers.DateField(source="user.date_of_birth")
    is_active = serializers.BooleanField(source="user.is_active")

    registered_at = serializers.DateTimeField(
        source="user.created_at",
        help_text="Date et heure d'inscription du compte",
    )
    membership_requested_at = serializers.DateTimeField(
        source="created_at",
        help_text="Date et heure de la soumission de la demande d'adhésion",
    )
    membership_validated_at = serializers.DateTimeField(
        source="membership_date",
        help_text="Date et heure de la validation par l'admin",
    )

    class Meta:
        model = MemberProfile
        fields = [
            "matricule", "first_name", "last_name", "email", "phone",
            "sex", "date_of_birth",
            "id_document_type", "id_document_number",
            "city", "commune", "region", "neighborhood",
            "profession", "motivation",
            "photo", "id_document_scan",
            "membership_status",
            "registered_at", "membership_requested_at", "membership_validated_at",
            "registration_source", "is_active",
        ]
