"""
WorkSphere HR - Employee API Serializers
"""
from rest_framework import serializers
from apps.employees.models import (
    Employee, Department, Designation, Location, CostCenter,
    EmergencyContact, EmployeeBank, EmployeeStatutory, EmployeeFamily,
    EmployeeEducation, EmployeeExperience, EmployeeSkill
)


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head', 'parent', 'description', 'is_active',
                  'employee_count', 'created_at']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Designation
        fields = ['id', 'name', 'department', 'department_name', 'grade', 'level', 'is_active']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'code', 'address', 'city', 'state', 'country', 'pincode',
                  'latitude', 'longitude', 'geo_fence_radius', 'is_active']


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['id', 'name', 'relationship', 'phone', 'alternate_phone', 'address', 'is_primary']


class EmployeeBankSerializer(serializers.ModelSerializer):
    masked_account = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeBank
        fields = ['id', 'bank_name', 'account_number', 'masked_account', 'account_type',
                  'ifsc_code', 'branch_name', 'is_primary', 'is_verified']
        extra_kwargs = {'account_number': {'write_only': True}}

    def get_masked_account(self, obj):
        acc = obj.account_number
        if len(acc) > 4:
            return 'X' * (len(acc) - 4) + acc[-4:]
        return acc


class EmployeeStatutorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeStatutory
        fields = ['id', 'pan_number', 'aadhaar_number', 'uan_number', 'pf_number',
                  'esi_number', 'pt_number', 'passport_number', 'passport_expiry',
                  'driving_license_number', 'driving_license_expiry',
                  'is_pf_applicable', 'is_esi_applicable', 'is_pt_applicable']


class EmployeeFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFamily
        fields = ['id', 'name', 'relationship', 'date_of_birth', 'is_nominee',
                  'nominee_percentage', 'is_dependent']


class EmployeeEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEducation
        fields = ['id', 'degree', 'institution', 'field_of_study', 'start_year',
                  'end_year', 'grade', 'is_highest']


class EmployeeSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSkill
        fields = ['id', 'skill_name', 'proficiency', 'years_of_experience']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_name = serializers.CharField(source='designation.name', read_only=True)
    reporting_manager_name = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_code', 'employee_id', 'full_name', 'first_name', 'last_name',
            'official_email', 'mobile', 'department_name', 'designation_name',
            'reporting_manager_name', 'employment_type', 'status', 'joining_date',
            'profile_photo_url', 'location',
        ]

    def get_reporting_manager_name(self, obj):
        if obj.reporting_manager:
            return obj.reporting_manager.get_full_name()
        return None

    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
        return None


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Full employee details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerProperty(read_only=True)
    years_of_service = serializers.IntegerProperty(read_only=True)
    department_details = DepartmentSerializer(source='department', read_only=True)
    designation_details = DesignationSerializer(source='designation', read_only=True)
    location_details = LocationSerializer(source='location', read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    bank_accounts = EmployeeBankSerializer(many=True, read_only=True)
    statutory = EmployeeStatutorySerializer(read_only=True)
    family_members = EmployeeFamilySerializer(many=True, read_only=True)
    education = EmployeeEducationSerializer(many=True, read_only=True)
    skills = EmployeeSkillSerializer(many=True, read_only=True)
    reporting_manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_reporting_manager_name(self, obj):
        if obj.reporting_manager:
            return obj.reporting_manager.get_full_name()
        return None


# Fix the IntegerProperty issue
class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Full employee details"""
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()
    department_details = DepartmentSerializer(source='department', read_only=True)
    designation_details = DesignationSerializer(source='designation', read_only=True)
    location_details = LocationSerializer(source='location', read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    bank_accounts = EmployeeBankSerializer(many=True, read_only=True)
    statutory = EmployeeStatutorySerializer(read_only=True)
    family_members = EmployeeFamilySerializer(many=True, read_only=True)
    education = EmployeeEducationSerializer(many=True, read_only=True)
    skills = EmployeeSkillSerializer(many=True, read_only=True)
    reporting_manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_age(self, obj):
        return obj.age

    def get_years_of_service(self, obj):
        return obj.years_of_service

    def get_reporting_manager_name(self, obj):
        if obj.reporting_manager:
            return obj.reporting_manager.get_full_name()
        return None


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
