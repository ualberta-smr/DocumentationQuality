import itertools


class DocCodeExample:
    id_iter = itertools.count()

    def __init__(self, example: str, url: str):
        self.id = next(self.id_iter)
        self.example = example
        self.url = url
