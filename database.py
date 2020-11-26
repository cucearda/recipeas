from recipe import Recipe

class Database:
    def __init__(self):
        self.recipes = {}
        self._lats_recipe_key = 0

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