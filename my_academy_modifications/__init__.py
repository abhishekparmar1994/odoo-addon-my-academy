import os

# Auto-inject wkhtmltopdf bin path on Windows if not already present in PATH
wkhtml_path = r"C:\Program Files\wkhtmltopdf\bin"
if os.path.exists(wkhtml_path) and wkhtml_path not in os.environ['PATH']:
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + wkhtml_path

from . import models
from . import controllers
