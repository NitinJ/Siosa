import os


class Resource:
    LINE_FEED = '\n'

    @staticmethod
    def _get_path(filename):
        """
        Args:
            filename:
        """
        return os.path.join(os.path.dirname(__file__), filename)

    @staticmethod
    def get(resource):
        """
        Args:
            resource:
        """
        f = open(Resource._get_path(resource), 'r')
        return f.read().split(Resource.LINE_FEED)
