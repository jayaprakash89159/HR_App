"""WorkSphere HR - Attendance Serializers"""
from rest_framework import serializers
from .models import Attendance, ODApplication, ShortTimeOff

class AttendanceSerializer(serializers.ModelSerializer):
    working_hours_display = serializers.ReadOnlyField()
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'

class ODApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ODApplication
        fields = '__all__'

class ShortTimeOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortTimeOff
        fields = '__all__'
