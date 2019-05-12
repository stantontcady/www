import sys
if sys.version_info[0] < 3:
	raise Exception
sys.path.insert(0, '/var/www/lmo-stc/')
from lmo_stc import app as application
