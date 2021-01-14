import user
class Post:
    def __init__(self, post_id, content, title, user_id, likecount, commentcount, postdate):
        self.content = content
        self.post_id = post_id
        self.title = title
        self.creator = user.get_user_by_id(user_id)
        self.likecount = likecount
        self.commentcount = commentcount
        self.postdate = postdate