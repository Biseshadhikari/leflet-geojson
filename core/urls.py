from django.urls import path
from . import views

urlpatterns = [
    path('', views.map, name='map'),
        # path('api/municipal-map-data/', views.municipal_map_data, name='municipal-map-data'),

]