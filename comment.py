import user
class Comment:
    def __init__(self, comment_id,content, user_id, post_id, likecount):
        self.user = user.get_user_by_id(user_id)
        self.likecount = likecount
        self.content = content
        self.post_id = post_id
        self.id = comment_id