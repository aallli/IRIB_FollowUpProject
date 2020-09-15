from django.contrib import admin
from django.contrib import messages
from .models import Supervisor, User
from django.db.transaction import atomic
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from jalali_date.admin import ModelAdminJalaliMixin
from IRIB_FollowUpProject.admin import BaseModelAdmin
from django.utils.translation import ugettext_lazy as _
from EIRIB_FollowUp.utils import save_user, delete_user
from django.contrib.auth.admin import UserAdmin as _UserAdmin


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
            'fields': (('supervisor', 'email'))}),
        (_('Important dates'), {
            'fields': (('last_login_jalali', 'date_joined_jalali'),)}),
        (_('Permissions'), {
            'fields': (('is_staff', 'is_superuser'), 'groups', 'user_permissions'), }),
        (_('Sensitive Info'), {'fields': ('password',)}),
    )
    list_display = ['username', 'first_name', 'last_name', 'access_level', 'supervisor', 'last_login_jalali']
    list_display_links = ['username', 'first_name', 'last_name', 'access_level', 'supervisor', 'last_login_jalali']
    list_filter = ('supervisor', 'access_level', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ['last_login_jalali', 'date_joined_jalali']
    change_form_template = 'admin/custom/change_form.html'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_secretary and not request.user.is_superuser:
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
            self.message_user(request, _('Error in creating/updating user in MS Acceess Database'), messages.WARNING)


    def save_related(self, request, form, formsets, change):
        user = form.instance
        super(UserAdmin, self).save_related(request, form, formsets, change)
        self.set_groups(user)

    def set_groups(self, user):
        if user.is_secretary:
            user.groups.add(get_object_or_404(Group, name='Operators'))
            user.groups.remove(get_object_or_404(Group, name='Users'))
        else:
            user.groups.add(get_object_or_404(Group, name='Users'))
            user.groups.remove(get_object_or_404(Group, name='Operators'))

    def delete_model(self, request, obj):
        try:
            try:
                delete_user(obj)
            except Exception as e:
                self.message_user(request, _('Error in deleting user from MS Acceess Database'), messages.WARNING)

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
                    self.message_user(request, _('Error in deleting user from MS Acceess Database'), messages.WARNING)
                obj.delete()
            except Exception as e:
                messages.set_level(request, messages.ERROR)
                messages.error(request, e)
