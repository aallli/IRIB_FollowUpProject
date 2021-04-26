import pyodbc
from .models import User
from threading import Timer
from django.conf import settings
from django.utils import timezone
from IRIB_FollowUp.models import AccessLevel
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from .models import Enactment, Session, Assigner, Subject, Actor, Supervisor

msgid = _('welcome')
settings.WITHOUT_SESSION_TITLE = _('[Without session]')
settings.WITHOUT_ASSIGNER_TITLE = _('[Without assigner]')
settings.WITHOUT_SUBJECT_TITLE = _('[Without subject]')
settings.WITHOUT_SUPERVISOR_TITLE = _('[Without supervisor]')
msgid = _('Admin Interface')
msgid = _('Theme')
msgid = _('Themes')
msgid = _('Email address')
msgid = _('Hold down “Control”, or “Command” on a Mac, to select more than one.')
msgid = _('First, enter a username and password. Then, you’ll be able to edit more user options.')
msgid = _('The two password fields didn’t match.')
msgid = _(
    'Please enter your old password, for security’s sake, and then '
    'enter your new password twice so we can verify you typed it in '
    'correctly.')
msgid = _(
    'Raw passwords are not stored, so there is no way to see this '
    'user’s password, but you can change the password using '
    '<a href="{}">this form</a>.'
)

tries = 0
max_try = 50
max_data = 7
data_loaded = pow(2, max_data) - 1
conn = None


def get_sessions():
    global data_loaded
    try:
        Session.objects.all().delete()
        query = '''
                SELECT DISTINCT tblmosavabat.jalaseh
                FROM tblmosavabat
               '''
        result = execute_query(query)
        for r in result:
            Session.objects.get_or_create(
                name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, '', ' '] else r.jalaseh)
    finally:
        data_loaded ^= 1


def get_assigners():
    global data_loaded
    Assigner.objects.all().delete()
    try:
        query = '''
                SELECT DISTINCT tblmosavabat.gooyandeh
                FROM tblmosavabat
               '''
        result = execute_query(query)
        for r in result:
            Assigner.objects.get_or_create(
                name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, '', ' '] else r.gooyandeh)
    finally:
        data_loaded ^= 2


def get_subjects():
    global data_loaded
    try:
        Subject.objects.all().delete()
        query = '''
                SELECT DISTINCT tblmosavabat.muzoo
                FROM tblmosavabat
               '''
        result = execute_query(query)
        for r in result:
            Subject.objects.get_or_create(
                name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, '', ' '] else r.muzoo)
    finally:
        data_loaded ^= 4


def get_actors():
    global data_loaded
    try:
        Actor.objects.all().delete()
        query = '''
                SELECT tblUser.FName, tblUser.LName, tblUser.Moavenat
                FROM tblUser
               '''
        result = execute_query(query)
        for r in result:
            try:
                supervisor = None
                supervisor = get_object_or_404(Supervisor, name=r.Moavenat)
            except:
                pass
            Actor.objects.get_or_create(fname=r.FName, lname=r.LName, supervisor=supervisor)
    finally:
        data_loaded ^= 8


def get_supervisors():
    global data_loaded
    try:
        Supervisor.objects.all().delete()
        query = '''
                SELECT tblUser.Moavenat
                FROM tblUser
               '''
        result = execute_query(query)
        for r in result:
            Supervisor.objects.get_or_create(
                name=settings.WITHOUT_SUPERVISOR_TITLE if r.Moavenat in [None, '', ' '] else r.Moavenat)
    finally:
        data_loaded ^= 16
        actors = Timer(1, get_actors)
        actors.start()


def get_user_queries():
    global data_loaded
    try:
        users = execute_query('SELECT * FROM tblUser;')
        for u in users:
            try:
                user = User.objects.get(user__username=u.username)
                if user:
                    user.query_name = u.openningformP
                    command = 'SELECT * from %s' % user.query_name
                    result = execute_query(command)
                    user.query = [r.ID for r in result]

                if user.secretary_query_name:
                    command = 'SELECT * from %s' % user.secretary_query_name
                    try:
                        result = execute_query(command)
                        user.secretary_query = list(result[0])
                    except Exception:
                        user.secretary_query = None
                else:
                    user.secretary_query = None

                user.save()
            except:
                pass
    finally:
        data_loaded ^= 32


def get_enactments():
    global data_loaded, max_data, tries, max_try

    if data_loaded != pow(2, max_data - 1) - 1:
        if tries == max_try:
            data_loaded = pow(2, max_data) - 1
            tries = -1
            return
        tries += 1
        enactments = Timer(5, get_enactments)
        enactments.start()
        return

    command = 'SELECT * from tblmosavabat'
    try:
        result = execute_query(command)
        for r in result:
            try:
                enact = Enactment.objects.get_or_create(row= r.ID)
                enactment = enact[0]
                if enact[1]:
                    enactment.result = r.natije
                    enactment._review_date =r.review_date or timezone.now()

                enactment.description = r.sharh
                enactment.subject = Subject.objects.get(name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, ''] else r.muzoo)
                enactment.first_actor = Actor.objects.filter(lname=r.peygiri1).first()
                enactment.second_actor = Actor.objects.filter(lname=r.peygiri2).first()
                enactment._date = r.date or timezone.now()
                enactment.follow_grade = r.lozoomepeygiri
                enactment.session = Session.objects.get(
                        name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh)
                enactment.assigner = Assigner.objects.get(
                        name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, ''] else r.gooyandeh)
                enactment.save()
            except Exception as e:
                print(e)

    except Exception as e:
        print(e)
        tries = -1
        return
    finally:
        data_loaded ^= 64


def update_data():
    global data_loaded, tries, conn
    data_loaded = 0
    tries = 0

    try:
        conn = mdb_connect(settings.DATABASES['access-followup']['NAME'])
    except:
        tries = -1
        return

    sessions = Timer(1, get_sessions)
    sessions.start()

    assigners = Timer(1, get_assigners)
    assigners.start()

    subjects = Timer(1, get_subjects)
    subjects.start()

    supervisors = Timer(1, get_supervisors)
    supervisors.start()

    enactments = Timer(5, get_enactments)
    enactments.start()

    user_queries = Timer(1, get_user_queries)
    user_queries.start()


def data_loading():
    global data_loaded, max_data, tries, conn
    loading = data_loaded != pow(2, max_data) - 1
    if (not loading or tries == -1) and conn:
        conn.close()
        conn = None
    return loading, tries == -1


def user_exists(user_name):
    result = execute_query('SELECT * FROM tblUser WHERE tblUser.username=?;', (user_name))
    return len(result) > 0


def save_user(user):
    try:
        _user = User.objects.get(user=user)
    except:
        _user = User.objects.create(user=user, query_name=user.username)

    if user_exists(user.username):
        query = '''
                UPDATE tblUser
                SET tblUser.FName = ?
                , tblUser.LName = ?
                , tblUser.Moavenat = ?
                , tblUser.openningformP = ?
                , tblUser.AccessLevelID = ?
                , tblUser.envan = ?
                , tblUser.username = ?
                WHERE username = ?
               '''
        params = (user.first_name, user.last_name, user.supervisor.name if user.supervisor else '', _user.query_name,
                  1 if user.access_level == AccessLevel.USER else 4, str(user.title()), user.username, user.username)
        execute_query(query, params, update=True)
    else:
        query = '''
                INSERT INTO tblUser (FName, LName, Password, Moavenat, openningformP, AccessLevelID, envan, P, username)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
        params = (user.first_name, user.last_name, user._password, user.supervisor.name if user.supervisor else '',
                  _user.query_name, 1 if user.access_level == AccessLevel.USER else 4, str(user.title()), 'p',
                  user.username)
        execute_query(query, params, insert=True)


def delete_user(user):
    query = '''
            DELETE FROM tblUser
            WHERE tblUser.username = ?
            '''
    params = (user.username)
    execute_query(query, params, delete=True)


def mdb_connect(db_file, user='admin', password='', old_driver=False):
    driver_ver = '*.mdb'
    if not old_driver:
        driver_ver += ', *.accdb'

    odbc_conn_str = ('DRIVER={Microsoft Access Driver (%s)}'
                     ';DBQ=%s;UID=%s;PWD=%s' %
                     (driver_ver, db_file, user, password))

    return pyodbc.connect(odbc_conn_str)


def execute_query(query, params=None, update=None, insert=None, delete=None):
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)

    if update:
        conn.commit()
        result = _("Update failed.") if cur.rowcount == -1 else _("Successful update.")
    elif insert:
        conn.commit()
        cur.execute('SELECT @@IDENTITY;')
        result = cur.fetchone()[0]
    elif delete:
        conn.commit()
        result = _("Delete failed.") if cur.rowcount == -1 else _("Successful delete.")
    else:
        result = cur.fetchall()

    cur.close()
    return result
