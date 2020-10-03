import xlrd
from django.conf import settings


def get_excel_sheet():
    wb = xlrd.open_workbook(settings.DATABASES['excel-payment']['NAME'])
    return wb.sheet_by_index(0)
