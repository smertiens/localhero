import sys
from ._base import BasePlugin

class VueCLIPlugin(BasePlugin):
    
    handles = ['vue-cli']
    server_conf = None

    def __init__(self, server_conf):
        self.server_conf = server_conf

    def get_command(self):
        cmd = 'npm run serve'

        port = self.server_conf.get('port', None)

        if port is not None:
            # works only for vue cli 3.x
            cmd = cmd + ' -- --port %s' % port

        # workaround for https://stackoverflow.com/questions/43465086/env-node-no-such-file-or-directory-in-mac
        if sys.platform == 'darwin':
            cmd = 'export PATH="$PATH:"/usr/local/bin && ' + cmd

        

        return cmd

    def before_run(self):
        pass
