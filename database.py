from recipe import Recipe
from discussion import Discussion
from ingredient import Ingredient
import user
import psycopg2
import datetime

class Database:
    def __init__(self):
        pass

    def add_user(self, username, hashed, nickname, karma, date):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            if( not user.get_user(username) ):
                cur.execute("INSERT INTO users (username, password, nickname, register_date, karma) VALUES (%s, %s, %s, %s, %s)", (username, hashed, nickname, date, karma))
                conn.commit()
                return True
            else:
                return False

    def add_ingredient(self, ingredient_name):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("""SELECT * FROM ingredients WHERE ingredient_name= (%s) """, (ingredient_name,))

            ingredient_existance = cur.fetchone()

            if(ingredient_existance):
                return False
            else:
                cur.execute("""INSERT INTO ingredients (ingredient_name) VALUES (%s) """, (ingredient_name,))
                conn.commit()
                return True

    def add_tool(self, tool_name):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()

            cur.execute("SELECT * FROM tools WHERE tool_name= (%s)", (tool_name,))

            tool_existance = cur.fetchone()
            if(tool_existance):
                return False
            else:
                cur.execute("INSERT INTO tools (tool_name) VALUES (%s)", (tool_name,))
                conn.commit()
                return True
    
    def get_ingredients(self):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()

            cur.execute("SELECT * FROM ingredients")
            ingredients = cur.fetchall()
        return ingredients

    def get_tools(self):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()

            cur.execute("SELECT * FROM tools")
            tools = cur.fetchall()
        return tools

    def create_recipe(self, body, title, ingredient_ids, tool_ids, current_user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO recipes (title, content, user_id, triedcount, likecount, ingredientcount) VALUES (%s, %s, %s, 0, 0, 0) RETURNING id;", (title, body, current_user_id))
            recipe_id = cur.fetchone()

            for ingredient_id in ingredient_ids:
                cur.execute("INSERT INTO ingredient_mapper (ingredient_id, recipe_id) VALUES (%s, %s)", (ingredient_id, recipe_id))

            for tool_id in  tool_ids:
                cur.execute("INSERT INTO tool_mapper (tool_id, recipe_id) VALUES (%s, %s)", (tool_id, recipe_id))

            cur.execute("SELECT COUNT(ingredient_id) FROM ingredient_mapper WHERE recipe_id = %s", (recipe_id,))
            ing_count = cur.fetchone()
            cur.execute("UPDATE recipes SET ingredientcount= %s WHERE id = %s", (ing_count ,recipe_id))

            conn.commit()

    def get_recipes(self):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM recipes")
            recipes_list = []
            while True:
                tup = cur.fetchone()
                if tup == None:
                    break
                recipe = Recipe(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
                recipes_list.append(recipe)       
            return recipes_list


