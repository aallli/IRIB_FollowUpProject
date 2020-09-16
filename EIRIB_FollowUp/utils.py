from .models import User
from threading import Timer
from django.conf import settings
from django.utils import timezone
from IRIB_FollowUp.models import AccessLevel
from django.shortcuts import get_object_or_404
from IRIB_Shared_Lib.utils import execute_query
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
max_data = 6
data_loaded = pow(2, max_data) - 1


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

    Enactment.objects.all().delete()
    command = 'SELECT * from tblmosavabat'
    result = execute_query(command)
    try:
        Enactment.objects.bulk_create([Enactment(**{
            'row': r.ID,
            'description': r.sharh,
            'subject': Subject.objects.get(name=settings.WITHOUT_SUBJECT_TITLE if r.muzoo in [None, ''] else r.muzoo),
            'first_actor': Actor.objects.filter(lname=r.peygiri1).first(),
            'second_actor': Actor.objects.filter(lname=r.peygiri2).first(),
            '_date': r.date or timezone.now(),
            'follow_grade': r.lozoomepeygiri,
            'result': r.natije,
            'session': Session.objects.get(
                name=settings.WITHOUT_SESSION_TITLE if r.jalaseh in [None, ''] else r.jalaseh),
            'assigner': Assigner.objects.get(
                name=settings.WITHOUT_ASSIGNER_TITLE if r.gooyandeh in [None, ''] else r.gooyandeh),
            '_review_date': r.review_date or timezone.now()}) for r in result])
    except Exception as e:
        print(e)
        tries = -1
        return
    finally:
        data_loaded ^= 32


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


def update_data():
    global data_loaded, tries
    data_loaded = 0
    tries = 0

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


def data_loading():
    global data_loaded, max_data, tries
    return data_loaded != pow(2, max_data) - 1, tries == -1


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
