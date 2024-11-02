from django.utils.dateformat import DateFormat

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    Employee,
    Session
)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    # formatted_start_time = serializers.SerializerMethodField()
    # formatted_stop_time = serializers.SerializerMethodField()
    working_hours = serializers.ReadOnlyField()

    class Meta:
        model = Session
        fields = ['id', 'start_time', 'stop_time', 'working_hours']

    # def get_formatted_start_time(self, obj):
    #     formatted_start_time = obj.start_time
    #     if formatted_start_time:
    #         return DateFormat(formatted_start_time).format('d-m-Y, H:i')
    #     return None

    # def get_formatted_stop_time(self, obj):
    #     formatted_stop_time = obj.stop_time
    #     if formatted_stop_time:
    #         return DateFormat(formatted_stop_time).format('d-m-Y, H:i')
    #     return None
        

class SessionDashboardSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['id', 'name', 'start_time', 'active_session']
    
    def get_start_time(self, obj):
        last_session = Session.objects.filter(employee=obj).order_by('-start_time').first()
        if last_session:
            return DateFormat(last_session.start_time).format('d-m-Y, H:i')
        return None
    

class EmployeeHistorySerializer(serializers.Serializer):
    formatted_start_time = serializers.SerializerMethodField()
    formatted_stop_time = serializers.SerializerMethodField()
    working_hours = serializers.ReadOnlyField()

    class Meta:
        model = Session
        fields = ['id', 'start_time', 'stop_time', 'working_hours']

    def get_formatted_start_time(self, obj):
        formatted_start_time = obj.start_time
        if formatted_start_time:
            return DateFormat(formatted_start_time).format('d-m-Y, H:i')
        return None

    def get_formatted_stop_time(self, obj):
        formatted_stop_time = obj.stop_time
        if formatted_stop_time:
            return DateFormat(formatted_stop_time).format('d-m-Y, H:i')
        return None


class DownloadHistorySerializer(serializers.ModelSerializer):
    sessions = SessionSerializer(many=True, read_only=True, source='session_set')
    
    class Meta:
        model = Employee
        fields = ['id', 'name', 'active_service', 'active_session', 'sessions']

        
class BaseTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom restaurant and restaurant_name claims to the token
        # This will allow referencing the restaurant as authenticated user
        token['restaurant'] = user.restaurant.id
        token['restaurant_name'] = user.restaurant.name
        
        return token