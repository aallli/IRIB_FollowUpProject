from django.conf import settings
from .forms import GroupAdminForm
from .models import Supervisor, User
from django.db.transaction import atomic
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from IRIB_Shared_Lib.admin import BaseModelAdmin
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.translation import ugettext_lazy as _
from EIRIB_FollowUp.utils import save_user, delete_user
from django.contrib.auth.admin import UserAdmin as _UserAdmin, GroupAdmin as _GroupAdmin


@admin.register(Supervisor)
class SupervisorAdmin(BaseModelAdmin):
    model = Supervisor
    search_fields = ['name', ]


@admin.register(User)
class UserAdmin(ModelAdminJalaliMixin, _UserAdmin, BaseModelAdmin):
    fieldsets = (
        (_('Personal info'), {
            'fields': (('username', 'first_name', 'last_name', '_title'),
                       ('access_level', 'is_active'),)}),
        (_('Address Info'), {
            'fields': (('supervisor', ('personnel_number', 'national_code'), 'email'))}),
        (_('Important dates'), {
            'fields': (('last_login_jalali', 'date_joined_jalali'),)}),
        (_('Permissions'), {
            'fields': (('is_staff', 'is_superuser'), 'groups', 'user_permissions'), }),
        (_('Sensitive Info'), {'fields': ('password',)}),
    )
    list_display = ['username', 'national_code', 'personnel_number', 'first_name', 'last_name', 'access_level', 'supervisor', 'last_login_jalali']
    list_display_links = ['username', 'national_code', 'personnel_number', 'first_name', 'last_name', 'access_level', 'supervisor', 'last_login_jalali']
    list_filter = ('supervisor', 'access_level', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ['last_login_jalali', 'date_joined_jalali']
    change_form_template = 'admin/custom/change_form.html'

    def get_readonly_fields(self, request, obj=None):
        if (request.user.is_secretary or request.user.is_scoped_secretary) and not request.user.is_superuser:
            return self.readonly_fields + ['is_staff', 'is_superuser', 'groups', 'user_permissions']
        return self.readonly_fields

    @atomic
    def save_model(self, request, obj, form, change):
        password = None
        if not obj.pk:
            obj.is_staff = True
            password = obj._password

        super(UserAdmin, self).save_model(request, obj, form, change)

        if password:
            obj._password = password
        try:
            save_user(obj)
        except Exception as e:
            messages.set_level(request, messages.WARNING)
            messages.error(request, _('Error in creating/updating user in MS Acceess Database'))

    def save_related(self, request, form, formsets, change):
        user = form.instance
        super(UserAdmin, self).save_related(request, form, formsets, change)
        if 'access_level' in form.changed_data:
            self.set_groups(user)

    def set_groups(self, user):
        if user.is_secretary or user.is_scoped_secretary:
            if user.groups.filter(name__startswith='IRIB FU -').count():
                user.groups.add(get_object_or_404(Group, name=settings.IRIB_FU_OPERATOR_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.IRIB_FU_USER_GROUP_NAME))

            if user.groups.filter(name__startswith='EIRIB FU -').count():
                user.groups.add(get_object_or_404(Group, name=settings.EIRIB_FU_OPERATOR_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.EIRIB_FU_USER_GROUP_NAME))

            if user.groups.filter(name__startswith='KM -').count():
                user.groups.add(get_object_or_404(Group, name=settings.KM_OPERATOR_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.KM_USER_GROUP_NAME))

            if user.groups.filter(name__startswith='HR -').count():
                user.groups.add(get_object_or_404(Group, name=settings.HR_OPERATOR_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.HR_USER_GROUP_NAME))
        else:
            if user.groups.filter(name__startswith='IRIB FU -').count():
                user.groups.add(get_object_or_404(Group, name=settings.IRIB_FU_USER_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.IRIB_FU_OPERATOR_GROUP_NAME))

            if user.groups.filter(name__startswith='EIRIB FU -').count():
                user.groups.add(get_object_or_404(Group, name=settings.EIRIB_FU_USER_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.EIRIB_FU_OPERATOR_GROUP_NAME))

            if user.groups.filter(name__startswith='KM -').count():
                user.groups.add(get_object_or_404(Group, name=settings.KM_USER_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.KM_OPERATOR_GROUP_NAME))

            if user.groups.filter(name__startswith='HR -').count():
                user.groups.add(get_object_or_404(Group, name=settings.HR_USER_GROUP_NAME))
                user.groups.remove(get_object_or_404(Group, name=settings.HR_OPERATOR_GROUP_NAME))

    def delete_model(self, request, obj):
        try:
            try:
                delete_user(obj)
            except Exception as e:
                messages.set_level(request, messages.WARNING)
                messages.error(request, _('Error in deleting user from MS Acceess Database'))

            return super(UserAdmin, self).delete_model(request, obj)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            try:
                try:
                    delete_user(obj)
                except Exception as e:
                    messages.set_level(request, messages.WARNING)
                    messages.error(request, _('Error in deleting user from MS Acceess Database'))

                obj.delete()
            except Exception as e:
                messages.set_level(request, messages.ERROR)
                messages.error(request, e)


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(_GroupAdmin):
    form = GroupAdminForm
