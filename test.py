import os, time, signal
import logging
import subprocess, threading
import threading, shlex
from queue import Queue, Empty

import asyncio
import sys
from asyncio.subprocess import PIPE, STDOUT

stop = False

async def run_command(cmd, timeout=None):
    # start child process
    # NOTE: universal_newlines parameter is not supported
    process = await asyncio.create_subprocess_shell(
        cmd='source /Users/mephisto/projects/staycool-backend/.venv/bin/activate && flask run --port 5050',   # Python doc recommends str arg if shell=True
        #shell=True,
        env={'FLASK_APP': 'sc_backend_app.py'},
        cwd='/Users/mephisto/projects/staycool-backend',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # read line (sequence of bytes ending with b'\n') asynchronously
    while True:
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout)
        except asyncio.TimeoutError:
            pass
        else:
            if not line: # EOF
                break
            else:
                print(line)

    return await process.wait() # wait for the child process to exit


loop = asyncio.get_event_loop()
returncode = loop.run_until_complete(run_command(shlex.split('source /Users/mephisto/projects/staycool-backend/.venv/bin/activate && flask run --port 5050'),
                                                 timeout=1))
loop.close()

