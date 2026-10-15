"""
Django 项目主配置文件
项目名称：maneu
Django 版本：3.0
"""

import os

# ============================================================================
# 路径配置
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# 安全与调试配置
# ============================================================================

# 优先从环境变量读取，本地开发提供兜底值
SECRET_KEY = 'oju=dotp!)am+98zryygfio=py@j=rp4#a75l^$mk_d(g$ib55'


DEBUG = True

ALLOWED_HOSTS = ['*']

# ============================================================================
# 应用注册
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'maneu',
]

# ============================================================================
# 中间件配置
# ============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.UserMiddleware.UserMiddleware',   # 自定义 JWT 校验中间件
]

# ============================================================================
# URL 路由配置
# ============================================================================

ROOT_URLCONF = 'maneu.urls'

# ============================================================================
# 模板引擎配置
# ============================================================================

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

# ============================================================================
# WSGI 应用入口
# ============================================================================

WSGI_APPLICATION = 'maneu.wsgi.application'

# ============================================================================
# 数据库配置（MySQL）
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_NAME', 'maneu'),
        'HOST': os.environ.get('MYSQL_HOST', '127.0.0.1'),
        'PORT': int(os.environ.get('MYSQL_PORT', 3306)),
        'USER': os.environ.get('MYSQL_USER', 'maneu'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', '214772680'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ============================================================================
# 密码验证器
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# 国际化与本地化
# ============================================================================

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# ============================================================================
# 静态文件配置
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')      # collectstatic 输出目录
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]    # 开发时的额外静态目录

# ============================================================================
# 缓存配置（Redis）
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # 'PASSWORD': 'your_redis_password',
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
                'health_check_interval': 30,
            },
        },
        'KEY_PREFIX': 'maneu',
    }
}

# ============================================================================
# JWT 配置（PyJWT）
# ============================================================================
JWT_CONFIG = {
    # 签名密钥：直接复用 Django SECRET_KEY
    'SECRET_KEY': SECRET_KEY,

    # 签名算法
    'ALGORITHM': 'HS256',

    # 签发者（写在 payload.iss 里，解码时一并校验）
    'ISSUER': 'maneu',

    # Token 有效期（单位：秒）
    'ACCESS_TOKEN_LIFETIME': 3600,        # 1 小时
    'REFRESH_TOKEN_LIFETIME': 604800,     # 7 天

    # 请求头相关
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'AUTH_HEADER_TYPES': ('Bearer',),

    # ⭐ 路径含以下关键词 → 需要登录校验；其他一律放行
    #    所有需要登录的接口，URL 里带上 '/auth/' 即可自动生效
    'AUTH_URL_KEYWORDS': ['/auth/'],
}
