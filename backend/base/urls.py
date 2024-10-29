from django.urls import path

from .views import (
    BaseTokenObtainPairView,
    get_routes,
    get_employees,
    post_start_time,
    post_stop_time,
    get_start_times,
    create_employee,
    remove_employee,
    get_employee_session_history,
    
    download_csv
)

from rest_framework_simplejwt.views import (
    TokenRefreshView
)

urlpatterns = [
    path('', get_routes, name='get-routes'),
    
    path('api/token/', BaseTokenObtainPairView.as_view(), name='obtain-tokens'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh-tokens'),
    
    path('employees/', get_employees, name='get-employees'),
    path('employee/start-work/<int:pk>/', post_start_time, name='start-work'),
    path('employee/stop-work/<int:pk>/', post_stop_time, name='stop-work'),
    path('all-start-times/', get_start_times, name='start-times'),
    path('add-employee/', create_employee, name='add-employee'),
    path('employee/remove/<int:pk>/', remove_employee, name='remove-employee'),
    path('employee/history/<int:pk>/', get_employee_session_history, name='employee-history'),
    path('download-history/', download_csv, name='test')
]