__author__ = 'andrew.willis'

#Dummy Render Job for CRM

import random,time
error=random.randint(1,10)
if error>7:
    raise StandardError, 'error : dummy error state'
else:
    #render
    time.sleep(random.randint(1,10))