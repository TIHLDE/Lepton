from django.contrib import admin
from django.urls import path

from djproxy.views import HttpProxy


def generate_proxy(prefix, base_url="", verify_ssl=True):
    """Generates a ProxyClass based view that uses the passed base_url"""
    return type(
        "ProxyClass",
        (HttpProxy,),
        {
            "base_url": base_url,
            "reverse_urls": [(prefix, base_url)],
            "verify_ssl": verify_ssl,
        },
    )


def generate_routes(adminsite, config):
    """
    Generates a set of patterns and proxy views based on the passed config.
    Based on `djproxy`s implementation (https://github.com/thomasw/djproxy/blob/master/djproxy/urls.py)
    and adapted to add permissions-check through Django-admin.
    """
    routes = []

    for name, config in config.items():
        proxy = generate_proxy(
            config["prefix"], config["base_url"], config.get("verify_ssl", True)
        )
        proxy_view_function = proxy.as_view()

        proxy_view_function.csrf_exempt = config.get("csrf_exempt", True)

        routes.append(
            path(
                config["prefix"],
                admin.AdminSite.admin_view(adminsite, proxy_view_function),
                name=name,
            )
        )

    return routes


class FlowerAdminSite(admin.AdminSite):
    """
    Adds Flower as an admin-site by proxying the Flower Docker-container to /flower/admin.
    The page is locked behind Django permissions as we're extending Django Adminsite.
    This means that only superusers have permission to view the Flower dashboard
    """

    def get_urls(self):
        # This url refers to a Docker-container with the name "flower" which exposes port 5555
        base_url = "http://flower:5555/flower/admin/"
        urls = generate_routes(
            self,
            {
                "flower-dashboard": {"base_url": base_url, "prefix": "admin"},
                "flower-pages": {"base_url": base_url, "prefix": "admin/<path:url>"},
            },
        )
        urls += super().get_urls()
        return urls


flower_admin_site = FlowerAdminSite("flower_admin")
