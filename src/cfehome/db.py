from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Other settings ...

DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'ecommerce',
            'USER': 'dev-db',
            'PASSWORD': 'rI8BUmsTL6vN',
            'HOST': 'ep-divine-sun-a23huo6u.eu-central-1.aws.neon.tech',
            'PORT': 5432,
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
