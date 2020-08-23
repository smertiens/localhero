from ._base import BasePlugin

class NPMPlugin(BasePlugin):
    
    handles = ['npm']
    server_conf = None

    def __init__(self, server_conf):
        self.server_conf = server_conf

    def get_command(self):
        port = self.server_conf.get('port', 5000)
        cmd = 'npm run serve --port %s' % (port)
        return cmd

    def before_run(self):
        pass
