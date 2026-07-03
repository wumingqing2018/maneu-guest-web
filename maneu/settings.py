"""
Django 项目主配置文件
项目名称：maneu
Django 版本：3.0
"""

import os

# ============================================================================
# 路径配置
# ============================================================================

# 项目根目录（manage.py 所在目录的父目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# 安全与调试配置（生产环境必须修改）
# ============================================================================

# ⚠️ 生产环境务必从环境变量读取，绝对不能硬编码！！！
SECRET_KEY = 'oju=dotp!)am+98zryygfio=py@j=rp4#a75l^$mk_d(g$ib55'

# 调试模式：开发环境为 True，生产环境必须为 False
DEBUG = True

# 允许访问的主机列表，生产环境应替换为具体域名或 IP
ALLOWED_HOSTS = ['*']

# ============================================================================
# 应用注册
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',          # 后台管理
    'django.contrib.auth',           # 认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话管理
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件
    'maneu',                         # 自定义应用（主业务）
]

# ============================================================================
# 中间件配置（请求/响应处理链）
# ============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',     # 安全相关
    'django.contrib.sessions.middleware.SessionMiddleware',  # 会话支持
    'django.middleware.common.CommonMiddleware',         # 通用处理
    'django.middleware.csrf.CsrfViewMiddleware',         # CSRF 防护
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 用户认证
    'django.contrib.messages.middleware.MessageMiddleware',     # 消息处理
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # 点击劫持防护
    'common.UserMiddleware.UserMiddleware',               # 自定义用户中间件
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
        'DIRS': [BASE_DIR + '/templates'],   # 模板文件搜索路径（额外目录）
        'APP_DIRS': True,                    # 是否在应用内查找 templates 文件夹
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

# ⚠️ 生产环境建议从环境变量读取用户名、密码等敏感信息
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'maneu',                        # 数据库名称
        'HOST': '127.0.0.1',                    # 数据库主机地址
        'PORT': 3306,                           # 数据库端口
        'USER': 'maneu',                        # 数据库用户名
        'PASSWORD': '214772680',                # 数据库密码（应改为环境变量）
    }
}

# ============================================================================
# 密码验证器（用于用户密码强度校验）
# ============================================================================

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

# ============================================================================
# 国际化与本地化配置
# ============================================================================

LANGUAGE_CODE = 'zh-hans'          # 语言代码（简体中文）
TIME_ZONE = 'Asia/Shanghai'        # 时区（上海）
USE_I18N = True                    # 启用国际化
USE_L10N = True                    # 启用本地化格式（数字、日期等）
USE_TZ = False                     # 是否使用 UTC 时间（设为 False 则使用 TIME_ZONE）

# ============================================================================
# 静态文件配置（CSS、JS、图片等）
# ============================================================================

STATIC_URL = '/static/'            # 静态文件的 URL 前缀
STATIC_ROOT = "/static/"           # 收集静态文件的目标目录（生产环境用）
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # 额外的静态文件目录

"""
Static files config
https:#docs.djangoproject.com/en/3.0/howto/static-files/
"""
STATIC_URL = '/static/'
STATIC_ROOT = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# settings.py 末尾追加
JWT_CONFIG = {
    'SECRET_KEY': SECRET_KEY,  # 直接用 Django 的 SECRET_KEY
    'ALGORITHM': 'HS256',
    'ACCESS_TOKEN_LIFETIME': 300,  # 1 小时
    'REFRESH_TOKEN_LIFETIME': 604800,  # 7 天
}

# ============================================================================
# 缓存配置（使用 Redis）
# ============================================================================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",           # 缓存后端
        "LOCATION": "redis://127.0.0.1:6379/0",               # Redis 连接地址
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",  # 客户端类
            # "PASSWORD": "your_redis_password",               # Redis 密码（如有）
            "SOCKET_TIMEOUT": 5,                              # 读写超时（秒）
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",  # 启用数据压缩
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,                       # 连接池最大连接数
                "health_check_interval": 30                  # 连接健康检查间隔（秒）
            }
        },
        "KEY_PREFIX": "maneu"                                 # 所有缓存键的前缀，避免冲突
    }
}