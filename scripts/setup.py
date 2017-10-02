import pip
from shutil import copyfile

pip.main(['install', '-I', 'python-dateutil', 'boto3', 'pytz', 'icalendar', '--target', './lib'])
copyfile('./icalitup.py', './lib/icalitup.py')