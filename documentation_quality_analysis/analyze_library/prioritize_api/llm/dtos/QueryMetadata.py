class QueryMetadata:
    def __init__(self, post_id: str, post: str, api: str, library: str):
        self.post_id: str = post_id
        self.post: str = post
        self.api: str = api
        self.library: str = library
