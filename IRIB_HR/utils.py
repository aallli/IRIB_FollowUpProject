from threading import Timer
from django.conf import settings
import os, xlrd, tempfile, shutil
from IRIB_Shared_Lib.models import Month
from django.contrib.auth.models import Group
from EIRIB_FollowUp.models import User as _User
from .models import PaySlip, Bonus, BonusSubType
from IRIB_Auth.models import User, Supervisor, AccessLevel
from EIRIB_FollowUp.utils import mdb_connect, execute_query

tries = 0
max_try = 50
max_data = 1
data_loaded = pow(2, max_data) - 1


def import_users():
    wb = xlrd.open_workbook(os.path.join(settings.BASE_DIR, 'sms.xlsx'))
    sheet = wb.sheet_by_index(0)
    for i in range(1, sheet.nrows):
        user = sheet.row_values(i)
        supervisor = Supervisor.objects.update_or_create(name=user[6])[0]
        u = User.objects.filter(username=user[0])
        if u.count() == 0:
            u = User.objects.create(access_level=AccessLevel.USER, username=user[0])
            print("User Added: %s" % u.username)
        else:
            u = u[0]
            print("User Updated: %s" % u.username)

        u._title = user[1]
        u.first_name = user[2]
        u.last_name = user[3]
        u.is_staff = True
        u.supervisor = supervisor
        u.set_password(user[5])
        u.groups.add(Group.objects.get(name='KM - Users'))
        u.groups.add(Group.objects.get(name='HR - Users'))
        u.save()
        _u = _User.objects.filter(user__username=user[0])
        if _u.count() == 0:
            _User.objects.create(user=u, query_name=user[0])


def import_national_ids():
    wb = xlrd.open_workbook(os.path.join(settings.BASE_DIR, 'db\hoghoogh.xlsx'))
    sheet = wb.sheet_by_index(0)
    update_row = 1
    new_row = 1
    for i in range(1, sheet.nrows):
        try:
            user = sheet.row_values(i)
            u = User.objects.filter(username=user[0])
            if str(user[2]) == '1':
                if u.count() == 0:
                    print("%s- User %s not exists (%s)" % (new_row, user[0], user[1]))
                    new_row += 1
                    u = User.objects.create(access_level=AccessLevel.USER, username=user[0])
                    u.personnel_number = user[0]
                    u.national_code = user[1]
                    u._title = user[4]
                    u.first_name = user[11]
                    u.last_name = user[10]
                    u.is_staff = True
                    supervisor = Supervisor.objects.update_or_create(name=user[5])[0]
                    u.supervisor = supervisor
                    u.set_password(user[93])
                    u.groups.add(Group.objects.get(name='KM - Users'))
                    u.groups.add(Group.objects.get(name='HR - Users'))
                    u.save()
                    _u = _User.objects.filter(user__username=user[0])
                    if _u.count() == 0:
                        _User.objects.create(user=u, query_name=user[0])
                else:
                    print("%s- User %s is updating (%s)" % (update_row, user[0], user[1]))
                    update_row += 1
                    u = u[0]
                    u.personnel_number = user[0]
                    u.national_code = user[1]
                u.save()
        except Exception as e:
            print("%s (%s): %s" % (user[0], user[1], e))


def import_accord(bonus_sub_type_id):
    global data_loaded, tries, conn
    data_loaded = 0
    tries = 0

    try:
        conn = mdb_connect(settings.DATABASES['access-followup']['MDB'])
        query = '''
                SELECT tblAccord.the_year, tblAccord.the_month, tblAccord.final_bid, tblAccord.note, tblAccord.shomarekarmandi
                FROM tblAccord
               '''
        result = execute_query(query, conn=conn)
        type = BonusSubType.objects.get(pk=bonus_sub_type_id)
        for r in result:
            try:
                date = '%s/%s' % (r.the_year, r.the_month)
                user = User.objects.get(username=r.shomarekarmandi)
                Bonus.objects.get_or_create(type=type, user=user, _date=date, amount=r.final_bid, description=r.note)
            except:
                pass
    except:
        pass


def dump_uploaded_file(source):
    fd, filepath = tempfile.mkstemp(prefix=source.name, dir=settings.FILE_UPLOAD_TEMP_DIR)
    with open(filepath, 'wb') as dest:
        shutil.copyfileobj(source, dest)
    return filepath


def update_data(request):
    global data_loaded, tries
    data_loaded = 0
    tries = 0
    if request.method == 'POST' and 'file' in request.FILES:
        excel_file = request.FILES['file']
        try:
            excel_file = dump_uploaded_file(excel_file)
            wb = xlrd.open_workbook(excel_file)
            sheet = wb.sheet_by_index(0)
            for i in range(1, sheet.nrows):
                payment = sheet.row_values(i)
                try:
                    kwargs = dict(
                        national_id=int(payment[0]),
                        last_name=payment[1],
                        first_name=payment[2],
                        operation=payment[3],
                        overtime_working=payment[4],
                        basic_salary=payment[6],
                        special_allowance=payment[7],
                        post_allowance=int(payment[8]) + int(payment[14]) + int(payment[18]),
                        supplementary_allowance=payment[9],
                        overtime=payment[10],
                        food_cost=payment[11],
                        children_allowance=payment[12],
                        spouse_salary=payment[13],
                        housing_salary=payment[15],
                        etc=int(payment[16]),
                        difference=int(payment[17]),
                        insurance=payment[19],
                        tax=payment[20],
                        loan_installments=int(payment[21]),
                        contract_type=payment[27],
                        working_place=payment[28],
                        department=payment[29],
                        month=Month(str(int(payment[31]))[4:6]),
                        year=str(int(payment[31]))[:4],
                        account_no='-',
                        insurance_no='-',
                        job_title='-',
                        grocery_salary=0,
                        mobile_salary=0,
                        supplementary_insurance=0,
                        leave_balance=0,
                        atieh_balance=0,
                        refah_balance=0,
                    )

                    try:
                        kwargs['national_id'] = str(int(kwargs['national_id']))
                    except:
                        pass

                    try:
                        user = User.objects.get(national_code=kwargs['national_id'])
                        kwargs['personnel_id'] = user.personnel_number
                    except:
                        pass

                    payslip = PaySlip.objects.filter(national_id=kwargs['national_id'], month=kwargs['month'], year=kwargs['year'])
                    payslip.delete()
                    PaySlip.objects.create(**kwargs)
                except:
                    pass
        except:
            tries = -1
            return

        def clean_temp(file):
            if os.path.exists(file):
                os.remove(file)

        wb.release_resources()
        r = Timer(600.0, clean_temp, (excel_file,))
        r.start()
        data_loaded = 1


def data_loading():
    global data_loaded, max_data, tries
    loading = data_loaded != pow(2, max_data) - 1
    return loading, tries == -1
