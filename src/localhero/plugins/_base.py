class BasePlugin:

    SHUTDOWN_STRATEGY_INT = 0

    def get_command(self):
        raise Exception('BasePlugin.get_command() has to be overriden by child class.')

    def before_run(self):
        pass

    def get_shutdown_strategy(self):
        return self.SHUTDOWN_STRATEGY_INT