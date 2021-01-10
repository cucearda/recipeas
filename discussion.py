class Discussion:
    likes = None
    def __init__(self, user, content, comments, header):
        self.content = content
        self.user = user
        self.comments = comments
        self.header = header