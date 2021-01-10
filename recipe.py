import user
class Recipe:
    def __init__(self, recipe_id, title, description, creator_id, triedcount, likecount, ingredientcount):
        self.title = title
        self.description = description
        self.ingredientcount = ingredientcount
        self.creator = user.get_user_by_id(creator_id)
        self.recipe_id = recipe_id
        self.likecount = likecount
        self.triedcount = triedcount