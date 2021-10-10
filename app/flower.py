from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from djproxy.views import HttpProxy

# csrf_exempt doesn't work and the website therefore doesn't work :(
# @method_decorator(csrf_exempt, name='dispatch')
class FlowerProxyView(HttpProxy):
    base_url = 'http://flower:5555/flower/admin/'

class FlowerAdminSite(admin.AdminSite):

     def get_urls(self):
        #  proxy_view_function = FlowerProxyView.as_view()
        #  proxy_view_function.csrf_exempt = True
         from django.urls import path
         urls = [
             path(r'admin/', csrf_exempt(self.admin_view(FlowerProxyView.as_view()))),
             path(r'admin/<path:url>/', csrf_exempt(self.admin_view(FlowerProxyView.as_view())))
            #  path(r'admin/', csrf_exempt(self.admin_view(proxy_view_function))),
            #  path(r'admin/<path:url>/', csrf_exempt(self.admin_view(proxy_view_function)))
         ]
         urls += super().get_urls()
         return urls

flower_admin_site = FlowerAdminSite("flower_admin")