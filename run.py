import nightlite
import time
import datetime

while True:
	d = datetime.datetime.now()
	nightlite.processMinute(d.hour, d.minute)
	time.sleep(30)

