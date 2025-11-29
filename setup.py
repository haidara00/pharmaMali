
APP = ['waitress_server.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    # Includes & packages help ensure py2app bundles required modules
    'includes': ['waitress', 'reportlab', 'openpyxl', 'django'],
    'packages': ['pharmagestion', 'inventory', 'sales'],
    # Include templates and static as resources so the app can serve them
    'resources': ['templates', 'static'],
    'plist': {
        'CFBundleName': 'PharmaGestion',
        'CFBundleShortVersionString': '1.0',
    },
    # If you find missing modules at runtime, add them here.
}

if __name__ == '__main__':
    setup(
        app=APP,
        name='PharmaGestion',
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )

APP = ['waitress_server.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': False,
    # Includes & packages help ensure py2app bundles required modules
    'includes': ['waitress', 'reportlab', 'openpyxl', 'django'],
    'packages': ['pharmagestion', 'inventory', 'sales'],
    # Include templates and static as resources so the app can serve them
    'resources': ['templates', 'static'],
    'plist': {
        'CFBundleName': 'PharmaGestion',
        'CFBundleShortVersionString': '1.0',
    },
}

setup(
    app=APP,
    name='PharmaGestion',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
