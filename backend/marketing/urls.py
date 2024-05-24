from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


#router = DefaultRouter()
#router.register(r'brands', views.BrandAPIView)

urlpatterns = [
    #path('', include(router.urls)),
    path('brands/',views.BrandAPIView.as_view(),name='brands'),
    #path('product/create/',views.create_product,name='create_product'),
    #path('product/persona/',views.create_persona,name='create_persona')
]
