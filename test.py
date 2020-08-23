import os, time, sys, signal
import logging
import subprocess, threading
import threading
from queue import Queue, Empty

class OutputCollector(threading.Thread):

    stdout_q = Queue()
    stdout = None

    def __init__(self, stdout):
        super().__init__()
        self.stdout = stdout

    def run(self):
        while True:
            if (line := self.stdout.readline()) != '':
                self.stdout_q.put(line)
                print(line)
            else:
                break

class Test(threading.Thread):

    _stop = False
    proc = None

    def stop(self):
        print('Stopping')
        self._stop = True

    def run(self):

        _stop = False

        self.proc = subprocess.Popen(
            #args='python3 testproc.py',
            args='source /Users/mephisto/projects/staycool-backend/.venv/bin/activate && flask run --port 5050',   # Python doc recommends str arg if shell=True
            shell=True,
            env={'FLASK_APP': 'sc_backend_app.py'},
            cwd='/Users/mephisto/projects/staycool-backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True               # stdout as text not as byte stream
        )

        sto = OutputCollector(self.proc.stdout)
        sto.start()

        while (res := self.proc.poll()) is None:
            #try: print(sto.stdout_q.get_nowait())
            #except Empty: pass 
            if (line := self.proc.stdout.readline()) is not None:
                print(line)

        print('Finished process with %s' % res)
        
t = Test()
t.start()
print('Starting')
time.sleep(3)
t.proc.terminate()
#t.stop()