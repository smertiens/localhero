import yaml
import os
import logging
import subprocess, threading
from plugins import flask, npm

def process_variables(s: str, vars: dict) -> str:
    # TODO: proper regex
    for k, v in vars.items():
        s = s.replace('$'+k, v)
    
    return s

class ServerConfig:

    data = {}

    def __init__(self, data):
        self.data = data

    def get(self, k, d = None)->any:
        if k in self.data:
            return self.data[k]
        else:
            return d

class Config:

    servers = {}

    def __init__(self):
        self.servers = {}
    
    @staticmethod
    def get_config_file():
        f = os.path.realpath(os.path.join(os.path.dirname(__file__), 'config.yaml'))

        if os.path.exists(f):
            return f
        else:
            raise IOError('Config file "%s" not found' % f)

    def load_yaml(self, filename: str):
        
        with open(filename, 'r') as fp:
            try:
                servers = yaml.load(fp, Loader=yaml.SafeLoader)['servers']

                for name, conf in servers.items():
                    self.servers[name] = ServerConfig(conf)

            except Exception as e:
                raise Exception('Could not load config file "%s": %s' % (filename, str(e)))


    def get_servers(self) -> dict:
        return self.servers

class ServerRunnerEnvironment:

    plugins = []

    def __init__(self):
        self.plugins = [flask.FlaskPlugin, npm.NPMPlugin]


class ServerRunner(threading.Thread):

    conf = None
    env = None
    cmd = ''
    _on_output_updated = None
    running = False
    intent_to_stop = False
    output = ''

    def __init__(self, conf: ServerConfig, env: ServerRunnerEnvironment):
        super().__init__()

        self.conf = conf
        self.env = env
        self.intent_to_stop = False
        self.running = False

        # setup logging
        self.get_logger().addHandler(logging.StreamHandler())
        self.get_logger().setLevel(logging.DEBUG)

    def on_output_updated(self, cb: callable):
        self._on_output_updated = cb

    def get_logger(self) -> logging.Logger:
        return logging.getLogger(self.__module__)

    def stop(self):
        self.intent_to_stop = True

    def run(self):

        cmd = ''
        found_plugin = False
        self.intent_to_stop = False

        # find plugin to handle the config
        for plugin in self.env.plugins:
            if self.conf.get('type', '') in plugin.handles:
                self.get_logger().info('Using "%s" for type "%s"' % (plugin.__class__.__name__, self.conf.get('type')))
                plugin_inst = plugin(self.conf)
                cmd = plugin_inst.get_command()

                # stop looking for plugin
                found_plugin = True
                break

        if not found_plugin:
            raise Exception('Could not find a plugin to handle type "%s"' % self.conf.get('type'))

        cwd = os.path.realpath(self.conf.get('dir', '.'))

        if self.conf.get('venv', None) is not None:
            venv_dir = process_variables(self.conf.get('venv'), {'dir': cwd})
            venv_dir = os.path.join(venv_dir, 'bin', 'activate')
            cmd = 'source %s && %s' % (venv_dir, cmd)

        
        logging.getLogger(self.__module__).debug('Running command "%s"' % cmd)
       
        proc = subprocess.Popen(
            args=cmd,               # Python doc recommends str arg if shell=True
            shell=True,
            env=self.conf.get('env', {}),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True               # stdout as text not as byte stream
        )

        while (res := proc.poll()) is None:
            if self.intent_to_stop:
                self.get_logger().info('Sending SIGTERM...')
                proc.terminate()
                self.intent_to_stop = False

            if (line := proc.stdout.readline()) is not None:
                self.output += line + '\n'

        self.running = False
        self.get_logger().info('Server process stopped.')

'''
class ServerStack:

    conf = None
    plugins = []

    def __init__(self):
        self.conf = Config()
        self.conf.load_yaml(Config.get_config_file())

        self.plugins = [flask.FlaskPlugin]

        # setup logging
        self.get_logger().addHandler(logging.StreamHandler())
        self.get_logger().setLevel(logging.DEBUG)


    def get_logger(self) -> logging.Logger:
        return logging.getLogger(self.__module__)
    
    def run_server(self, name: str, server_conf: ServerConfig, cb = None):

        # find plugin to handle the config
        for plugin in self.plugins:
            if server_conf.get('type', '') in plugin.handles:
                self.get_logger().info('Using "%s" for type "%s"' % (plugin.__class__.__name__, server_conf.get('type')))
                plugin_inst = plugin(server_conf)
                cmd = plugin_inst.get_command()

                proc = ServerProcess(server_conf, cmd)
                proc.on_output_updated = cb
                plugin_inst.before_run()
                proc.start()

                # stop looking for plugin
                break
'''