
class Component():
    def __init__(self, name: str):
        self.name = name


class File:
    def __init__(self, path, component):
        self.path = path
        self.component = component

    def get(self):
        return {'path': self.path, 'component': self.component}
