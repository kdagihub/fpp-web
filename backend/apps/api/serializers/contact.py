from rest_framework import serializers

from apps.contact.models import ContactMessage


class PublicContactSerializer(serializers.ModelSerializer):
    """Formulaire de contact public — validation stricte."""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]

    def validate_message(self, value):
        if len(value) > 5000:
            raise serializers.ValidationError("Le message ne doit pas dépasser 5000 caractères.")
        return value

    def validate_subject(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Le sujet doit contenir au moins 3 caractères.")
        return value


class AdminContactListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "subject", "is_read", "created_at"]


class AdminContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id", "name", "email", "phone", "subject", "message",
            "is_read", "read_at", "created_at",
        ]
        read_only_fields = fields
