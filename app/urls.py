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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("rest_framework.urls")),
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
]
