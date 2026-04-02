from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import CanViewDashboard
from apps.content.models import Article
from apps.contact.models import ContactMessage
from apps.members.models import MemberProfile


class AdminDashboardView(APIView):
    """KPI du dashboard admin."""

    permission_classes = [IsAuthenticated, CanViewDashboard]

    def get(self, request):
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)

        members_qs = MemberProfile.objects.all()
        validated_qs = members_qs.filter(membership_status=MemberProfile.StatusChoices.VALIDATED)

        total_members = validated_qs.count()
        pending_members = members_qs.filter(membership_status=MemberProfile.StatusChoices.PENDING).count()
        recent_members_30d = members_qs.filter(created_at__gte=last_30_days).count()
        recent_members_7d = members_qs.filter(created_at__gte=last_7_days).count()

        members_by_city = list(
            validated_qs
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        members_by_status = list(
            members_qs
            .values("membership_status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        members_by_sex = list(
            validated_qs
            .values("user__sex")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        total_articles = Article.objects.filter(
            status=Article.StatusChoices.PUBLISHED,
            deleted_at__isnull=True,
        ).count()
        draft_articles = Article.objects.filter(
            status=Article.StatusChoices.DRAFT,
            deleted_at__isnull=True,
        ).count()

        unread_contacts = ContactMessage.objects.filter(is_read=False).count()
        total_contacts = ContactMessage.objects.count()

        period = request.query_params.get("period", "30")
        try:
            period_days = int(period)
        except (ValueError, TypeError):
            period_days = 30
        period_start = now - timedelta(days=period_days)

        from django.db.models.functions import TruncDate
        members_evolution = list(
            members_qs
            .filter(created_at__gte=period_start)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        return Response({
            "members": {
                "total_validated": total_members,
                "pending": pending_members,
                "recent_30d": recent_members_30d,
                "recent_7d": recent_members_7d,
                "by_city": members_by_city,
                "by_status": members_by_status,
                "by_sex": members_by_sex,
                "evolution": [
                    {"date": entry["date"].isoformat(), "count": entry["count"]}
                    for entry in members_evolution
                ],
            },
            "articles": {
                "total_published": total_articles,
                "drafts": draft_articles,
            },
            "contacts": {
                "total": total_contacts,
                "unread": unread_contacts,
            },
        })
