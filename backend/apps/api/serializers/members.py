from rest_framework import serializers

from apps.members.models import MemberProfile


class AdminMemberListSerializer(serializers.ModelSerializer):
    """Liste admin paginee — champs essentiels."""

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone")
    sex = serializers.CharField(source="user.sex")
    is_active = serializers.BooleanField(source="user.is_active")

    class Meta:
        model = MemberProfile
        fields = [
            "id", "matricule", "first_name", "last_name", "email", "phone", "sex",
            "city", "commune", "membership_status", "is_active",
            "created_at",
        ]


class AdminMemberDetailSerializer(serializers.ModelSerializer):
    """Fiche detaillee d'un membre + info user + roles actifs."""

    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone")
    sex = serializers.CharField(source="user.sex")
    date_of_birth = serializers.DateField(source="user.date_of_birth")
    avatar = serializers.ImageField(source="user.avatar")
    is_active = serializers.BooleanField(source="user.is_active")
    registered_at = serializers.DateTimeField(source="user.created_at")
    active_roles = serializers.SerializerMethodField()

    class Meta:
        model = MemberProfile
        fields = [
            "id", "matricule",
            "first_name", "last_name", "email", "phone", "sex", "date_of_birth", "avatar",
            "id_document_type", "id_document_number", "id_document_scan", "photo",
            "city", "commune", "region", "neighborhood",
            "profession", "address", "motivation",
            "membership_status", "membership_date", "registration_source",
            "is_active", "registered_at", "active_roles",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_active_roles(self, obj):
        roles = obj.user.party_roles.filter(is_active=True).select_related("role", "zone")
        return [
            {
                "role_name": ur.role.name,
                "role_level": ur.role.level,
                "zone_name": ur.zone.name if ur.zone else None,
                "assigned_at": ur.created_at.isoformat() if ur.created_at else None,
            }
            for ur in roles
        ]


class AdminMemberUpdateSerializer(serializers.ModelSerializer):
    """Admin : modification des champs du profil membre."""

    class Meta:
        model = MemberProfile
        fields = [
            "city", "commune", "region", "neighborhood",
            "profession", "address",
        ]


class AdminMemberStatusSerializer(serializers.Serializer):
    """Admin : changement de statut adhesion."""

    status = serializers.ChoiceField(choices=MemberProfile.StatusChoices.choices)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
