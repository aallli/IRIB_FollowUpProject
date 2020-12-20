from threading import Timer
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from EIRIB_FollowUp.utils import execute_query
from EIRIB_FollowUp.models import User as _User
from django.contrib.auth.backends import ModelBackend
from IRIB_Auth.models import User, Title, AccessLevel, Supervisor


class EIRIBBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = self.get_user_by_username(username)
        except User.DoesNotExist:
            return

        if user.check_password(password) and self.user_can_authenticate(user):
            if not user.is_secretary:
                user_query = Timer(1, self.get_user_query(_User.objects.get_or_create(user=user)[0]))
                user_query.start()
            return user
        else:
            if not user.is_superuser:
                user.delete()

    def get_user_by_username(self, user_name):
        try:
            result = execute_query('SELECT * FROM tblUser WHERE tblUser.username=?;', (user_name))
            if len(result) == 0:
                raise User.DoesNotExist

            result = result[0]
            user = None
            try:
                user = get_user_model()._default_manager.get_by_natural_key(user_name)
            except:
                pass

            title = None
            for t in enumerate(Title):
                if t[1].label == result.envan:
                    title = t[1]
                    break
            title = title or Title.MR
            if result.AccessLevelID == 4:
                access_level = AccessLevel.SECRETARY
            else:
                access_level = AccessLevel.USER

            supervisor = Supervisor.objects.get_or_create(name=result.Moavenat)[0]

            if user:
                user.first_name = result.FName
                user.last_name = result.LName
                user.supervisor = supervisor
                # @todo: Better to consider scoped secretary access level in excel
                # user.access_level = access_level
                user._title = title
            else:
                user = User.objects.create(username=user_name, first_name=result.FName, last_name=result.LName,
                                           supervisor=supervisor, access_level=access_level, _title=title,
                                           is_staff=True)

            self.set_groups(user)
            user.set_password(result.Password)
            user.save()

            _user = _User.objects.get_or_create(user=user)[0]
            _user.query_name = result.openningformP
            _user.save()
        except User.DoesNotExist:
            raise User.DoesNotExist

        return user

    def get_user_query(self, user):
        command = 'SELECT * from %s' % user.query_name
        try:
            result = execute_query(command)
            user.query = [r.ID for r in result]
            user.save()
        except:
            pass

    def set_groups(self, user):
        if user.is_secretary or user.is_scoped_secretary:
            try:
                user.groups.add(Group.objects.get(name=settings.EIRIB_FU_OPERATOR_GROUP_NAME))
            except:
                pass
            try:
                user.groups.remove(Group.objects.get(name=settings.EIRIB_FU_USER_GROUP_NAME))
            except:
                pass
        else:
            try:
                user.groups.remove(Group.objects.get(name=settings.EIRIB_FU_OPERATOR_GROUP_NAME))
            except:
                pass
            try:
                user.groups.add(Group.objects.get(name=settings.EIRIB_FU_USER_GROUP_NAME))
            except:
                pass
