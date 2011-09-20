from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'main_page.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^s/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)

urlpatterns += patterns('',
    url(r'^socket.io/', include('realtime.urls')),
)

urlpatterns += patterns('',
    url(r'^(?P<shortcut>.*)$', 'main_page.views.redirection'),
)

