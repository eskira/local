from distutils.core import setup
import py2exe
 
# setup(console=['jama_to_shm_change.py'])

option = {
    'bundle_files':1,
    'compressed': True
}
setup(
    options = {'py2exe': option},
    console=['jama_to_shm_change.py'],
    zipfile = 'jama_to_shm_change.zip', 
    )
