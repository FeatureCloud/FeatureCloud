
class FCException(Exception):
    """
    Base class for FeatureCloud exceptions.
    """
    default_detail = 'an error occurred'

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail

        self.detail = detail

    def __str__(self):
        return str(self.detail)


class DockerNotAvailable(FCException):
    default_detail = 'Docker daemon is not available. Please make sure Docker is started.'


class ControllerOffline(FCException):
    def __init__(self, url=None):
        super().__init__(f'Could not access controller on URL: {url}')


class ContainerNotFound(FCException):
    def __init__(self, name=None):
        super().__init__(f'Container not found: {name}')
