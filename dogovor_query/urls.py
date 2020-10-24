"""mobile_query URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from .views import *
from .forms import *
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path('manager/', index, name='query_list'),
    path('manager/login', specialist_login, name='specialist_login'),
    path('manager/logout', specialist_logout, name='specialist_logout'),
    path('manager/api/requests/get', get_requests, name='get_requests'),
    path('manager/api/status/<str:action>/<int:request_pk>', get_update_status, name='get_update_status'),
    path('', main_page, name='request_form'),
    path('api/query/get', get_query_position, name='user_request_info'),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
