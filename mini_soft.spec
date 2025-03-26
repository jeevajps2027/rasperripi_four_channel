# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# Environment variables
os.environ["DJANGO_SETTINGS_MODULE"] = "mini_soft.settings"

# Collect 'channels' submodules
hiddenimports = collect_submodules('channels')

block_cipher = None

a = Analysis(
    ['manage.py'],
    pathex=['C:/Users/itzpr.DESKTOP-EUQC32B/Desktop/mini_soft/mini_soft'],  # Path to your project folder
    binaries=[],
    
    datas=[
        ('app/templates/app', 'app/templates/app'),
        ('app/static', 'app/static'),
        ('app/views', 'app/views'),
        ('staticfiles', 'staticfiles'),
        ('app/migrations', 'app/migrations'),
        ('mini_soft/asgi.py', 'mini_soft/asgi.py'),  # Include ASGI file
        ('mini_soft/settings.py', 'mini_soft/settings.py'),  # Include settings
    ],

    hiddenimports=[
        *hiddenimports,  # Unpack the collected submodules
        'whitenoise.middleware',
        'serial.tools.list_ports',
        'pyserial',
        'serial',
        'kaleido',
        'whitenoise',
        'channels_redis.core',
        'channels_redis',
        'redis',
        'django.core.asgi',
        'django.core.wsgi',  # Add this for WSGI fallback
        'mini_soft.asgi',    # Explicitly include ASGI module
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mini_soft',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='C:\\Users\\itzpr.DESKTOP-EUQC32B\\Desktop\\mini_soft\\mini_soft\\app\\static\\images\\Gauge.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX compression
    upx_exclude=[],
    name='mini_soft'
)
