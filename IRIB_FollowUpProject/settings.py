"""
Django settings for IRIB_FollowUpProject project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'irt=69_xpf6#pzm&c4s%ogrt*t!i5oy-=i*70yw0@agjjbr8mx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# admin info
VERSION = '1.14.5'
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
    'excel-payment': {
        'NAME': os.environ.get('EXCEL_DATABASES_NAME', default=os.path.join(BASE_DIR, 'db\حقوق.xlsx')),
    }
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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'IRIB_Shared_Lib/static'),
    MEDIA_ROOT,
    TEMPLATES[0]['DIRS'][0],
]

AUTH_USER_MODEL = 'IRIB_Auth.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'EIRIB_FollowUp.backends.EIRIBBackend',
]

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

NAVIGATED_MODELS = ['EIRIB_FollowUp_session', 'EIRIB_FollowUp_assigner', 'EIRIB_FollowUp_subject',
                    'EIRIB_FollowUp_actor', 'EIRIB_FollowUp_supervisor', 'EIRIB_FollowUp_user',
                    'EIRIB_FollowUp_enactment',

                    'IRIB_FollowUp_sessionbase', 'IRIB_FollowUp_session', 'IRIB_FollowUp_enactment',
                    'IRIB_FollowUp_subject', 'IRIB_FollowUp_group',

                    'Knowledge_Management_committeemember', 'Knowledge_Management_category',
                    'Knowledge_Management_indicator', 'Knowledge_Management_activity',
                    'Knowledge_Management_subcategory', 'Knowledge_Management_assessmentcardtable',
                    'Knowledge_Management_personalcardtable',

                    'IRIB_HR_payslip',
                    ]

# EIRIB Followup Configurations
EIRIB_FU_OPERATOR_GROUP_NAME = 'EIRIB FU - Operators'
EIRIB_FU_USER_GROUP_NAME = 'EIRIB FU - Users'

# IRIB Followup Configurations
IRIB_FU_OPERATOR_GROUP_NAME = 'IRIB FU - Operators'
IRIB_FU_USER_GROUP_NAME = 'IRIB FU - Users'

# Knowledge Management Configurations
KM_OPERATOR_GROUP_NAME = 'KM - Operators'
KM_USER_GROUP_NAME = 'KM - Users'

# EIRIB HR Configurations
HR_OPERATOR_GROUP_NAME = 'HR - Operators'
HR_USER_GROUP_NAME = 'HR - Users'
