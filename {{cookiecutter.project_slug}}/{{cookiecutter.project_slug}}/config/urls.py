import django.views.static
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='base.html')),
    url(r'^admin/', admin.site.urls),
    {%- if cookiecutter.use_djangocms == 'y' %}
    url(r'^', include('cms.urls')),
    {%- endif %}
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + staticfiles_urlpatterns() + urlpatterns
