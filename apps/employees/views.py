"""WorkSphere HR - Employee API Views"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.db.models import Q

from .models import Employee, Department, Designation, Location


def serialize_employee(emp, detail=False):
    base = {
        'id': str(emp.id),
        'employee_id': emp.employee_id,
        'first_name': emp.first_name,
        'last_name': emp.last_name,
        'full_name': emp.get_full_name(),
        'email': emp.user.email if emp.user else '',
        'department': {'id': str(emp.department.id), 'name': emp.department.name} if emp.department else None,
        'designation': {'id': str(emp.designation.id), 'name': emp.designation.name} if emp.designation else None,
        'location': {'id': str(emp.location.id), 'name': emp.location.name} if emp.location else None,
        'status': emp.status,
        'date_of_joining': emp.date_of_joining.isoformat() if emp.date_of_joining else None,
    }
    if detail:
        base.update({
            'gender': emp.gender,
            'phone': emp.phone,
            'date_of_birth': emp.date_of_birth.isoformat() if emp.date_of_birth else None,
            'address': emp.permanent_address,
            'emergency_contact_name': emp.emergency_contact_name,
            'emergency_contact_phone': emp.emergency_contact_phone,
            'bank_account_number': emp.bank_account_number,
            'bank_name': emp.bank_name,
            'ifsc_code': emp.ifsc_code,
        })
    return base


@extend_schema(request=None, responses=None)
class EmployeeListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not getattr(request.user, 'can_manage_employees', False) and not getattr(request.user, 'is_admin_portal', False):
            return Response({'error': 'Permission denied'}, status=403)
        qs = Employee.objects.select_related('department', 'designation', 'location', 'user').order_by('first_name', 'last_name')
        search = request.query_params.get('search', '').strip()
        dept = request.query_params.get('department', '')
        emp_status = request.query_params.get('status', 'active')
        if search:
            qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(employee_id__icontains=search) | Q(user__email__icontains=search))
        if dept:
            qs = qs.filter(department_id=dept)
        if emp_status:
            qs = qs.filter(status=emp_status)
        return Response({'count': qs.count(), 'results': [serialize_employee(e) for e in qs[:200]]})


@extend_schema(request=None, responses=None)
class EmployeeDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            emp = Employee.objects.select_related('department', 'designation', 'location', 'user').get(id=pk)
        except Employee.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        # Employee can only see their own profile
        if not request.user.is_admin_portal:
            try:
                if emp != request.user.employee_profile:
                    return Response({'error': 'Permission denied'}, status=403)
            except Exception:
                return Response({'error': 'Permission denied'}, status=403)
        return Response(serialize_employee(emp, detail=True))


@extend_schema(request=None, responses=None)
class DepartmentListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        depts = Department.objects.filter(is_active=True).order_by('name')
        return Response([{'id': str(d.id), 'name': d.name, 'code': d.code} for d in depts])


@extend_schema(request=None, responses=None)
class DesignationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        desigs = Designation.objects.filter(is_active=True).select_related('department').order_by('department__name', 'name')
        dept_id = request.query_params.get('department')
        if dept_id:
            desigs = desigs.filter(department_id=dept_id)
        return Response([{'id': str(d.id), 'name': d.name, 'department': d.department.name} for d in desigs])


@extend_schema(request=None, responses=None)
class MyProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            emp = request.user.employee_profile
        except Exception:
            return Response({'error': 'No employee profile found'}, status=404)
        return Response(serialize_employee(emp, detail=True))

    def patch(self, request):
        try:
            emp = request.user.employee_profile
        except Exception:
            return Response({'error': 'No employee profile found'}, status=404)
        # Only allow updating safe self-service fields
        safe_fields = ['phone', 'emergency_contact_name', 'emergency_contact_phone',
                       'permanent_address', 'current_address', 'bank_account_number',
                       'bank_name', 'ifsc_code']
        for field in safe_fields:
            if field in request.data:
                setattr(emp, field, request.data[field])
        emp.save()
        return Response(serialize_employee(emp, detail=True))
