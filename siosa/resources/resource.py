import os


class Resource:
    LINE_FEED = '\n'

    @staticmethod
    def _get_path(filename):
        return os.path.join(os.path.dirname(__file__), filename)

    @staticmethod
    def get(resource):
        f = open(Resource._get_path(resource), 'r')
        return f.read().split(Resource.LINE_FEED)
