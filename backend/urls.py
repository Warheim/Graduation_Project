from django.urls import path

from backend.views import ShopUpdate

app_name = 'backend'
urlpatterns = [
    path('partner/update', ShopUpdate.as_view(), name='partner-update'),
]
