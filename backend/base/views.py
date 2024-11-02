from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.http import FileResponse

from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_201_CREATED,
)

from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Employee,
    Session
)

from .serializers import (
    EmployeeSerializer,
    SessionDashboardSerializer,
    EmployeeHistorySerializer,
    DownloadHistorySerializer,
    BaseTokenObtainPairSerializer
)

import io
import pandas as pd


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Name': 'get_routes',
            'Method': 'GET',
            'Description': 'Returns an overview of all endpoints'
        },
        {
            'Name': 'BaseTokenObtainPairView',
            'Method': 'POST', 
            'Description': 'Obtains an access and refresh token with custom claims'            
        },
        {
            'Name': 'get_employees',
            'Method': 'GET',
            'Description': 'Returns a list of active employees from the Employee model'
        },
        {
            'Name': 'create_employee',
            'Method': 'POST',
            'Description': 'Creates a new employee object in the Employee model'
        },
    ]
    return Response(routes)


class BaseTokenObtainPairView(TokenObtainPairView):
    serializer_class = BaseTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employees(request):
    if not request.user.is_authenticated:
        return Response({"error": "You are not authenticated"}, status=HTTP_401_UNAUTHORIZED)
    else:
        restaurant = request.user.restaurant
    
    employees = Employee.objects.filter(restaurant=restaurant, active_service=True)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_start_time(request, pk):
    
    if not request.user.is_authenticated:
        return Response({"error": "You are not authenticated"}, status=HTTP_401_UNAUTHORIZED)
    else:
        restaurant = request.user.restaurant
    
    employee = get_object_or_404(Employee, id=pk, restaurant=restaurant)
    
    active_session = Session.objects.filter(employee=employee, stop_time__isnull=True).exists()
    
    if active_session:
        return Response({"error": "Sesión ya activada"}, status=HTTP_400_BAD_REQUEST)
    Session.objects.create(employee=employee, start_time=timezone.now())
    employee.active_session = True
    employee.save()
    return Response({"message": "Start time registered successfully"}, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_stop_time(request, pk):
    restaurant = request.user.restaurant
    employee = get_object_or_404(Employee, id=pk, restaurant=restaurant)
    active_session = Session.objects.filter(employee=employee, stop_time__isnull=True).first()
    if not active_session:
        return Response({"error": "There is no active session"}, status=HTTP_400_BAD_REQUEST)
    active_session.stop_time = timezone.now()
    active_session.save()
    employee.active_session = False
    employee.save()
    return Response({"message": "End time registered successfully"}, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_start_times(request):
    if not request.user.is_authenticated:
        return Response({"error": "You are not authenticated"}, status=HTTP_401_UNAUTHORIZED)
    
    else:
        restaurant = request.user.restaurant
    
    employees = Employee.objects.filter(restaurant=restaurant, active_service=True)
    serializer = SessionDashboardSerializer(employees, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employee(request):
    if not request.user.is_authenticated:
        return Response({"error": "You are not authenticated"}, status=HTTP_401_UNAUTHORIZED)
    else:
        restaurant = request.user.restaurant
    
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        if Employee.objects.filter(name=serializer.validated_data["name"], restaurant=restaurant, active_service=True).exists():
            return Response({"error": "The employee already exists"}, status=HTTP_400_BAD_REQUEST)
        else: 
            serializer.save(restaurant=restaurant, active_service=True)
            return Response(serializer.data, status=HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        

@api_view(['DELETE'])    
@permission_classes([IsAuthenticated])
def remove_employee(request, pk):
    if not request.user.is_authenticated:
        return Response({"error": "You are not authenticated"}, status=HTTP_401_UNAUTHORIZED)
    else:
        restaurant = request.user.restaurant        
        
    try:
        employee = Employee.objects.get(pk=pk, restaurant=restaurant, active_service=True)
        employee.active_service = False
        employee.save()
        return Response({"message": "The employee has been removed"}, status=HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({"error": "The employee does not exist"}, status=HTTP_400_BAD_REQUEST)
    

class SessionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_session_history(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    sessions = Session.objects.filter(employee=employee).order_by('-start_time')

    paginator = SessionPagination()
    result_page = paginator.paginate_queryset(sessions, request)
    serializer = EmployeeHistorySerializer(result_page, many=True)

    return paginator.get_paginated_response({
        'employee_name': employee.name,  
        'sessions': serializer.data 
    })
    
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_csv(request):  

    restaurant = request.user.restaurant      
    employees = Employee.objects.filter(restaurant=restaurant)
    serializer = DownloadHistorySerializer(employees, many=True)
    
    df = pd.json_normalize(serializer.data, record_path="sessions", meta=["name"])
    df = df.reindex(columns=["name", "start_time", "stop_time", "working_hours"])
    df = df.rename(columns={
    "name": "employee",
    "start_time": "start_time",
    "stop_time": "end_time",
    "working_hours": "total_hours"
    })
    
    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['end_time'] = pd.to_datetime(df['end_time']).dt.strftime('%Y-%m-%d %H:%M:%S')

    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    response = FileResponse(buffer, as_attachment=True, filename="employee_session_history.csv")
    return response
    
