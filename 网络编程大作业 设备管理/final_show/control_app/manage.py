#!/usr/bin/env python
import os
import sys
from default.email import send_email
import subprocess
#========================
import time,threading
from default.client import client_model
#========================
def start_django():
    print("Go into the Django thread!")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "control_app.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    #send_email("850165905@qq.com","1234")
    start_django()
    # clientM= threading.Thread(target=client_model, name='clientM')
    # djangoM = threading.Thread(target=start_django, name='djangoM')
    # clientM.start()
    # djangoM.start()
    #
    # clientM.join()
    # djangoM.join()


