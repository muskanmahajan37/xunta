from __future__ import unicode_literals
from django.conf.urls import patterns, include, url
from django.contrib import admin
from mezzanine.core.views import direct_to_template
from homepage.views import HomepageList


admin.autodiscover()


urlpatterns = patterns("",
    url("^$", HomepageList.as_view(), name="home"),
    ("^admin/", include(admin.site.urls)),
    ("^", include("drum.links.urls")),
    ("^", include("juba.urls")),
    ("^", include("mezzanine.urls")),
)

# Adds ``STATIC_URL`` to the context.
handler500 = "mezzanine.core.views.server_error"
