import os

# Update to the root domain name for your site. Used for email verification link do not include trailing /
BASE_WEB_DOMAIN = os.environ.get('BASE_WEB_DOMAIN')
APP_LOG_PATH = os.environ.get('APP_LOG_PATH')

REQUIRE_EMAIL_VERIFY = os.environ.get('REQUIRE_EMAIL_VERIFY', 'False').lower() in ('true', '1', 't', 'y', 'yes')
REQUIRE_LOGIN = os.environ.get('REQUIRE_LOGIN', 'False').lower() in ('true', '1', 't', 'y', 'yes')

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')
DB_KEY3 = os.environ.get('DB_KEY3')

MAIL_HOST = os.environ.get('MAIL_HOST')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USER = os.environ.get('MAIL_USER')
MAIL_PASS = os.environ.get('MAIL_PASS')
REGMAIL_USER = os.environ.get('REGMAIL_USER')
ALERTMAIL_USER = os.environ.get('ALERTMAIL_USER')

RECAPTCHA_ENABLED = os.environ.get('RECAPTCHA_ENABLED', 'False').lower() in ('true', '1', 't', 'y', 'yes')
RECAPTCHA_SITEID = os.environ.get('RECAPTCHA_SITEID')
RECAPTCHA_KEY = os.environ.get('RECAPTCHA_KEY')

CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL')
