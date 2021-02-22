from threading import Timer
from .models import PaySlip
from django.conf import settings
import os, xlrd, tempfile, shutil
from IRIB_Shared_Lib.models import Month


def dump_uploaded_file(source):
    fd, filepath = tempfile.mkstemp(prefix=source.name, dir=settings.FILE_UPLOAD_TEMP_DIR)
    with open(filepath, 'wb') as dest:
        shutil.copyfileobj(source, dest)
    return filepath


def update_data(request):
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
                        month=Month(str(int(payment[30]))[2:4]),
                        year=str(int(payment[30]))[:2],
                        first_name=payment[2],
                        last_name=payment[1],
                        personnel_id=int(payment[0]),
                        account_no='-',
                        insurance_no='-',
                        department=payment[28],
                        working_place=payment[27],
                        job_title='-',
                        basic_salary=payment[6],
                        supplementary_allowance=payment[9],
                        operation=payment[3],
                        overtime_working=payment[4],
                        overtime=payment[10],
                        special_allowance=payment[7],
                        post_allowance=int(payment[8]) + int(payment[14]) + int(payment[17]),
                        children_allowance=payment[12],
                        etc=int(payment[16]),
                        grocery_salary=0,
                        housing_salary=payment[15],
                        spouse_salary=payment[13],
                        mobile_salary=0,
                        food_cost=payment[11],
                        insurance=payment[18],
                        tax=payment[19],
                        loan_installments=int(payment[20]),
                        supplementary_insurance=0,
                        contract_type=payment[26],
                        leave_balance=0,
                        atieh_balance=0,
                        refah_balance=0,
                    )

                    try:
                        kwargs['national_id'] = str(int(kwargs['national_id']))
                    except:
                        pass

                    try:
                        kwargs['personnel_id'] = str(int(kwargs['personnel_id']))
                    except:
                        pass

                    try:
                        kwargs['account_no'] = str(int(kwargs['account_no']))
                    except:
                        pass

                    try:
                        kwargs['insurance_no'] = str(int(kwargs['insurance_no']))
                    except:
                        pass

                    payslip = PaySlip.objects.filter(personnel_id=kwargs['personnel_id'], month=kwargs['month'],
                                                     year=kwargs['year'])
                    payslip.delete()
                    PaySlip.objects.create(**kwargs)
                except:
                    pass
        except:
            return

        def clean_temp(file):
            if os.path.exists(file):
                os.remove(file)

        wb.release_resources()
        r = Timer(600.0, clean_temp, (excel_file,))
        r.start()

