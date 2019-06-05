import sys
if sys.version_info[0] < 3:
	raise Exception
sys.path.insert(0, '/var/www/stc/')
from stc import app as application
