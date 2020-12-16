from recipe import Recipe
from discussion import Discussion

class Database:
    def __init__(self):
        self.recipes = {}
        self.discussions = {}
        self._lats_recipe_key = 0
        self._last_discussion_key = 0

    def add_recipe(self, recipe):
        self.recipes[self._lats_recipe_key] = recipe
        self._lats_recipe_key += 1
        return (self._lats_recipe_key)
    
    def delete_recipe (self, recipe_key):
        if recipe_key in self.recipes:
            del self.recipes[recipe_key]
        else:
            print("CAN'T DELETE RECIPE, KEY NOT FOUND")
        
    def get_recipe(self, recipe_key):
        recipe = self.recipes.get(recipe_key)
        if recipe is None:
            return None
        recipe_ = Recipe(recipe.name, recipe.description, recipe.main_ingridient)
        return recipe_
        
    def get_recipes(self):
        recipes = []
        for recipe_key, recipe in self.recipes.items():
            recipe_ = Recipe(recipe.name, recipe.description, recipe.main_ingridient)
            recipes.append((recipe_key, recipe_))
        return recipes

    def add_discussion(self, discussion):
        self.discussions[self._last_discussion_key] = discussion
        self._last_discussion_key += 1
        return (self._last_discussion_key)

    def delete_discussion (self, discussion_key):
        if discussion_key in self.discussions:
            del self.discussions[discussion_key]
        else:
            print("CAN'T DELETE DISCUSSION, KEY NOT FOUND")

    def get_discussion(self, discussion_key):
        discussion = self.discussions.get(discussion_key)
        if discussion is None:
            return None
        discussion_ = Discussion(discussion.user, discussion.content, discussion.likes, discussion.comments, discussion.header)
        return discussion_

    def get_discussions(self):
        discussions = []
        for discussion_key, discussion in self.discussions.items():
            discussion_ = Discussion(discussion.user, discussion.content, discussion.likes, discussion.comments, discussion.header)
            discussions.append((discussion_key, discussion_))
        return discussions