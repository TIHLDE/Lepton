"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Lepton API",
        default_version="v1",
        description="API for our Django backend",
        contact=openapi.Contact(email="teknologiminister@tihlde.org"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("rest_framework.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Our endpoints
    path("", include("app.career.urls")),
    path("", include("app.communication.urls")),
    path("", include("app.content.urls")),
    path("", include("app.group.urls")),
    path("", include("app.payment.urls")),
    path("auth/", include("app.authentication.urls")),
    path("badges/", include("app.badge.urls")),
    path("forms/", include("app.forms.urls")),
    path("galleries/", include("app.gallery.urls")),
    path("badges/", include("app.badge.urls")),
    path("kontres/", include("app.kontres.urls")),
    path("emojis/", include("app.emoji.urls")),
    path("codex/", include("app.codex.urls")),
    path("", include("app.feedback.urls")),
]
