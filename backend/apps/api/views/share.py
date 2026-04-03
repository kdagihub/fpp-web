"""
Endpoint de partage social — sert une page HTML minimale avec les balises
Open Graph / Twitter Card pour que les crawlers (WhatsApp, Facebook, Telegram,
Twitter) puissent générer un aperçu riche (image, titre, description).

Les vrais navigateurs sont redirigés vers la page SPA correspondante.
"""
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.html import escape
from django.views import View

from apps.content.models import Article, Event, ProgramSection

CRAWLERS = [
    "facebookexternalhit",
    "Facebot",
    "Twitterbot",
    "TelegramBot",
    "WhatsApp",
    "LinkedInBot",
    "Slackbot",
    "Discordbot",
    "vkShare",
    "Pinterest",
    "Googlebot",
]

OG_TEMPLATE = """<!DOCTYPE html>
<html lang="fr" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="utf-8">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:site_name" content="FPP — Front Patriotique Panafricain">
<meta property="og:locale" content="fr_FR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image}">
<title>{title}</title>
<meta http-equiv="refresh" content="0;url={redirect_url}">
</head>
<body>
<p>Redirection vers <a href="{redirect_url}">{title}</a>…</p>
</body>
</html>"""


def _is_crawler(request) -> bool:
    ua = request.META.get("HTTP_USER_AGENT", "")
    return any(bot.lower() in ua.lower() for bot in CRAWLERS)


def _build_absolute_media_url(request, path: str) -> str:
    if not path:
        return ""
    if path.startswith("http"):
        return path
    return request.build_absolute_uri(path)


def _build_og_response(request, *, title, description, image, redirect_url, og_type="article"):
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    canonical_url = redirect_url if redirect_url.startswith("http") else f"{frontend_url}{redirect_url}"

    if not _is_crawler(request):
        return HttpResponseRedirect(canonical_url)

    html = OG_TEMPLATE.format(
        og_type=escape(og_type),
        title=escape(title),
        description=escape(description[:300]),
        image=escape(image),
        canonical_url=escape(canonical_url),
        redirect_url=escape(canonical_url),
    )
    return HttpResponse(html, content_type="text/html; charset=utf-8")


class ShareArticleView(View):
    def get(self, request, slug):
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/actualites/{slug}"

        try:
            article = Article.objects.get(
                slug=slug,
                status=Article.StatusChoices.PUBLISHED,
                deleted_at__isnull=True,
            )
        except Article.DoesNotExist:
            return HttpResponseRedirect(redirect_url)

        image = ""
        if article.cover_image:
            image = _build_absolute_media_url(request, article.cover_image.url)

        return _build_og_response(
            request,
            title=article.title,
            description=article.summary,
            image=image,
            redirect_url=redirect_url,
            og_type="article",
        )


class ShareEventView(View):
    def get(self, request, slug):
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/agenda#{slug}"

        try:
            event = Event.objects.get(slug=slug, is_active=True)
        except Event.DoesNotExist:
            return HttpResponseRedirect(redirect_url)

        image = ""
        if event.cover_image:
            image = _build_absolute_media_url(request, event.cover_image.url)

        description = event.short_description or event.description[:200]
        if event.location:
            description += f" — {event.location}"
        if event.city:
            description += f", {event.city}"

        return _build_og_response(
            request,
            title=event.title,
            description=description,
            image=image,
            redirect_url=redirect_url,
            og_type="article",
        )


class ShareProgrammeView(View):
    def get(self, request, slug):
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/programme#{slug}"

        try:
            section = ProgramSection.objects.get(slug=slug, is_active=True)
        except ProgramSection.DoesNotExist:
            return HttpResponseRedirect(redirect_url)

        image = ""
        if section.cover_image:
            image = _build_absolute_media_url(request, section.cover_image.url)

        item_count = section.items.filter(is_active=True).count()
        description = section.description
        if item_count:
            description += f" — {item_count} mesures concrètes."

        return _build_og_response(
            request,
            title=f"{section.title} — Programme du FPP",
            description=description,
            image=image,
            redirect_url=redirect_url,
            og_type="article",
        )
