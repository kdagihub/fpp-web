from rest_framework import serializers

from apps.api.serializers.membership import validate_image_file
from apps.site_settings.models import SiteSettings


class PublicSiteSettingsSerializer(serializers.ModelSerializer):
    """Parametres publics — pas de champs sensibles."""

    class Meta:
        model = SiteSettings
        fields = [
            "site_name", "slogan",
            "president_name", "president_message", "president_photo",
            "whatsapp_number", "contact_email", "address",
            "facebook_url", "twitter_url", "instagram_url", "youtube_url",
            "logo", "hero_image", "hero_title", "hero_subtitle",
            "about_text", "vision_text", "values_text",
        ]


class AdminSiteSettingsSerializer(serializers.ModelSerializer):
    """Admin — tous les champs modifiables."""

    class Meta:
        model = SiteSettings
        fields = [
            "id",
            "site_name", "slogan",
            "president_name", "president_message", "president_photo",
            "whatsapp_number", "contact_email", "address",
            "facebook_url", "twitter_url", "instagram_url", "youtube_url",
            "logo", "hero_image", "hero_title", "hero_subtitle",
            "about_text", "vision_text", "values_text",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def validate_president_photo(self, value):
        if value:
            return validate_image_file(value, "Photo du président")
        return value

    def validate_logo(self, value):
        if value:
            return validate_image_file(value, "Logo")
        return value

    def validate_hero_image(self, value):
        if value:
            return validate_image_file(value, "Image hero")
        return value
