def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def abstractmethod(func_):
    def abstract_method(*args, **kwargs):
        raise Exception("In-implemented abstract method Exception!")

    return abstract_method
