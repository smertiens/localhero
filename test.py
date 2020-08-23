import os, time, sys, signal
import logging
import subprocess, threading
import threading
from queue import Queue, Empty

interupt = False

class Test(threading.Thread):

    def run(self):

        def test(buf, q: Queue):
            for line in buf:
                print(line)
                q.put(line)
            buf.close()
                
        proc = subprocess.Popen(
            args='python3 testproc.py',
            #args='source /Users/mephisto/projects/staycool-backend/.venv/bin/activate && flask run --port 5050',   # Python doc recommends str arg if shell=True
            shell=True,
            #env={'FLASK_APP': 'sc_backend_app.py'},
            #cwd='/Users/mephisto/projects/staycool-backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True               # stdout as text not as byte stream
        )

        q = Queue()
        t = threading.Thread(target=test, args=(proc.stdout, q))
        t.daemon = True # thread dies with the program
        t.start()


        while (res := proc.poll()) is None:
            global interupt

            try:
                print('>> %s' % q.get_nowait())
            except Empty:
                pass

            if interupt:
                interupt = False
                print('terminating')
                #proc.terminate()
                proc.send_signal(signal.SIGINT)
                #proc.send_signal(signal.SIGINT)
                #time.sleep(1)
                break

        print('Finished process with %s' % res)
        
t = Test()
#t.daemon = True
t.start()
print('Starting')
time.sleep(3)

interupt = True