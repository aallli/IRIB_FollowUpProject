"""
Django settings for IRIB_FollowUpProject project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'irt=69_xpf6#pzm&c4s%ogrt*t!i5oy-=i*70yw0@agjjbr8mx'
SSO_SALT = os.environ.get('SSO_SALT', default='5152')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# admin info
VERSION = '1.29.0'
ADMIN_TEL = os.environ.get('ADMIN_TEL', default='+98 21 2915 5120')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', default='admin@eirib.ir')
SITE_HEADER = _('EIRIB Administration System')
WITHOUT_SESSION_TITLE = None
WITHOUT_ASSIGNER_TITLE = None
WITHOUT_SUBJECT_TITLE = None
WITHOUT_SUPERVISOR_TITLE = None

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", default="localhost").split(" ")

# Application definition

INSTALLED_APPS = [
    # third party apps
    'admin_interface',
    'jalali_date',
    'colorfield',
    'django_resized',

    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my apps
    'IRIB_HR.apps.IribHrConfig',
    'IRIB_Auth.apps.IribAuthConfig',
    'IRIB_FollowUp.apps.IribFollowupConfig',
    'EIRIB_FollowUp.apps.EiribFollowupConfig',
    'IRIB_Shared_Lib.apps.IribSharedLibConfig',
    'Knowledge_Management.apps.KnowledgeManagementConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'IRIB_FollowUpProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'IRIB_FollowUpProject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DATABASES_HOST', default='127.0.0.1'),
        'PORT': os.environ.get('DATABASES_PORT', default='5432'),
        'NAME': os.environ.get('DATABASES_NAME', default='irib_followup'),
        'USER': os.environ.get('DATABASES_USER', default='postgres'),
        'PASSWORD': os.environ.get('DATABASES_PASSWORD', default='123'),
    },
    'access-followup': {
        'NAME': os.environ.get('ACCESS_DATABASES_NAME', default=os.path.join(BASE_DIR, 'db\db.mdb')),
        'USER': os.environ.get('ACCESS_DATABASES_USER', default='Administrator, System'),
        'PASSWORD': os.environ.get('ACCESS_DATABASES_PASSWORD', default='123456'),
    },
    'access-personnel': {
        'NAME': os.environ.get('ACCESS_PERSONNEL_DATABASES_NAME', default="AutoUpdater.exe"),
        'MDB': os.environ.get('ACCESS_PERSONNEL_MDB_NAME', default=r"\\172.16.226.174\personel$\Fajazi_backend.accdb"),
        'PATH': os.environ.get('ACCESS_PERSONNEL_DATABASES_PATH',
                               default=r"\\172.16.226.174\Fileserver\Omomi-Hamkaran-Moavenat\personel\bin"),
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'fa'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LANGUAGES = [
    ('en', _('En')),
    ('fa', _('Fa')),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "media/temp")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'IRIB_Shared_Lib/static'),
    MEDIA_ROOT,
    TEMPLATES[0]['DIRS'][0],
]

AUTH_USER_MODEL = 'IRIB_Auth.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Image sizes
MAX_SMALL_IMAGE_WIDTH = 150  # in pixel
MAX_SMALL_IMAGE_HEIGHT = 150  # in pixel
MAX_MEDIUM_IMAGE_WIDTH = 500  # in pixel
MAX_MEDIUM_IMAGE_HEIGHT = 500  # in pixel
MAX_LARGE_IMAGE_WIDTH = 1000  # in pixel
MAX_LARGE_IMAGE_HEIGHT = 1000  # in pixel

# Django-Resized image resizing tool
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg", 'JPEG': ".jpeg", 'GIF': ".gif", 'PNG': ".png"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = False

# django jalali datae defaults
JALALI_DATE_DEFAULTS = {
    'Strftime': {
        'date': '%y/%m/%d',
        'datetime': '%H:%M:%S _ %y/%m/%d',
    },
    'Static': {
        'js': [
            # loading datepicker
            'admin/js/django_jalali.min.js',
            # OR
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js',
            # 'admin/js/main.js',
        ],
        'css': {
            'all': [
                'admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css',
            ]
        }
    },
}

X_FRAME_OPTIONS = 'SAMEORIGIN'

MOBILE_VALIDATORS = (
    RegexValidator(
        regex=r'^(\+989\d{9})|^(09\d{9})$',
        message=_("Valid mobile format is either +989xxxxxxxxx or 09xxxxxxxxx")),
)

NAVIGATED_MODELS = ['EIRIB_FollowUp_session', 'EIRIB_FollowUp_assigner', 'EIRIB_FollowUp_subject',
                    'EIRIB_FollowUp_actor', 'EIRIB_FollowUp_supervisor', 'EIRIB_FollowUp_user',
                    'EIRIB_FollowUp_enactment',

                    'IRIB_FollowUp_sessionbase', 'IRIB_FollowUp_session', 'IRIB_FollowUp_enactment',
                    'IRIB_FollowUp_subject', 'IRIB_FollowUp_group',

                    'Knowledge_Management_committeemember', 'Knowledge_Management_category',
                    'Knowledge_Management_indicator', 'Knowledge_Management_activity',
                    'Knowledge_Management_subcategory', 'Knowledge_Management_assessmentcardtable',
                    'Knowledge_Management_personalcardtable',

                    'IRIB_HR_payslip', 'IRIB_HR_bonustype', 'IRIB_HR_bonus', 'IRIB_HR_bonussubtype',
                    'IRIB_HR_personalinquiry',
                    ]

# EIRIB Followup Configurations
EIRIB_FU_OPERATOR_GROUP_NAME = 'EIRIB FU - Operators'
EIRIB_FU_USER_GROUP_NAME = 'EIRIB FU - Users'

# IRIB Followup Configurations
IRIB_FU_OPERATOR_GROUP_NAME = 'IRIB FU - Operators'
IRIB_FU_USER_GROUP_NAME = 'IRIB FU - Users'
IRIB_FU_ = {
    'HQ_GROUP_NAME': 'سامانه پیگیری - حوزه ریاست',
    'CS_PLANNING_GROUP_NAME': 'سامانه پیگیری - برنامه ریزی فضای مجازی',
    'CS_LICENSE_GROUP_NAME': 'سامانه پیگیری - صدور مجوز فضای مجازی',
}

# Knowledge Management Configurations
KM_OPERATOR_GROUP_NAME = 'KM - Operators'
KM_USER_GROUP_NAME = 'KM - Users'

# IRIB HR Configurations
HR_OPERATOR_GROUP_NAME = 'HR - Operators'
HR_USER_GROUP_NAME = 'HR - Users'
HR_INQUIRY_GROUP_NAME = 'HR - Personal Inquiry'
HR_ = {
    'ADMINISTRATION_GROUP_NAME': 'HR - Administration',
    'FINANCIAL_GROUP_NAME': 'HR - Financial',
    'PLANNING_GROUP_NAME': 'HR - Planning',
}

HR_INQUIRY_ = {
    'OPERATOR_GROUP_NAME': 'HR - Personal Inquiry - Operator',
    'SECURITY_GROUP_NAME': 'HR - Personal Inquiry - Security',
    'HQ_GROUP_NAME': 'HR - Personal Inquiry - HQ',
}
