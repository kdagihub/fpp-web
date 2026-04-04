from rest_framework import serializers

from apps.site_settings.models import BureauMember


class PublicBureauMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BureauMember
        fields = ["id", "full_name", "title", "photo", "order"]
        read_only_fields = fields


class AdminBureauMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BureauMember
        fields = ["id", "full_name", "title", "photo", "order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
