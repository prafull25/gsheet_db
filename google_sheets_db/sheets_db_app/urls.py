from django.urls import path
from sheets_db_app.views import save_user_data

urlpatterns = [
    path('', save_user_data, name='save_user_data'),

]
