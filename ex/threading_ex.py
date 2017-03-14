import threading
import time
import logging

def non_daemon():
    time.sleep(5)
    print 'Test non-daemon'

t = threading.Thread(name='non-daemon', target=non_daemon)

t.start()

print("start")
t.join()
print("ends")
