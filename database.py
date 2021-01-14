from recipe import Recipe
from ingredient import Ingredient
from post import Post
from comment import Comment
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

    def create_post(self, body, title, user_id, date):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO posts (content, title, user_id, likecount, commentcount, postdate) VALUES (%s, %s, %s, 0, 0, %s)", (body, title, user_id, date))        
            conn.commit()
    
    def get_posts(self):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM posts ORDER BY id DESC")
            posts_list = []
            while True:
                tup = cur.fetchone()
                if tup == None:
                    break
                post = Post(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
                posts_list.append(post)
            return posts_list

    def get_post(self, post_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
            tup = cur.fetchone()
            post = Post(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
            return post

    def get_post_comments(self, post_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM comments WHERE post_id = %s ORDER BY id DESC", (post_id,))
            comments = []
            while True:
                tup = cur.fetchone()
                if tup == None:
                    break
                comment = Comment(tup[0], tup[1], tup[2], tup[3], tup[4])
                comments.append(comment)
            return comments

    def create_comment(self, post_id, content, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()        
            cur.execute("INSERT INTO comments (content, user_id, post_id, likecount) VALUES (%s, %s, %s, %s)", (content, user_id, post_id, 0))
            conn.commit()
    
    def update_post_commentcounts(self, post_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(id) FROM comments WHERE post_id = %s", (post_id,))       
            comment_count = cur.fetchone()[0]
            cur.execute("UPDATE posts SET commentcount = %s WHERE id= %s", (comment_count, post_id))
            conn.commit()

    def vote_post(self, post_id, user_id, vote_type, prev_vote): # This removes, creates and updates votes all together
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            if prev_vote == 0:
                cur.execute("INSERT INTO post_votes (vote_type, user_id, post_id) VALUES (%s, %s, %s)", (vote_type, user_id, post_id))
            elif prev_vote == vote_type:
                cur.execute("DELETE FROM post_votes WHERE vote_type = %s AND  user_id = %s AND post_id = %s", (vote_type, user_id, post_id))
            else:
                cur.execute("UPDATE post_votes SET vote_type = %s WHERE user_id = %s AND post_id = %s", (vote_type, user_id, post_id))

    def check_post_like_dislike(self, post_id, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM post_votes WHERE post_id = %s AND user_id = %s", (post_id, user_id))        
            tup = cur.fetchone()
            if tup:
                return tup[0] # 0th row is vote type 1 if like -1 if dislike
            else:
                return 0 # return 0 if vote doesn't exist

    def update_post_like_counts(self, post_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(vote_type) FROM post_votes WHERE post_id = %s ", (post_id,))        
            like_count = cur.fetchone()[0]
            if like_count== None:
                like_count = 0 
            cur.execute("UPDATE posts SET likecount = %s WHERE id = %s",(like_count, post_id))
    def get_recipes(self):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM recipes ORDER BY id DESC")
            recipes_list = []
            while True:
                tup = cur.fetchone()
                if tup == None:
                    break
                recipe = Recipe(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
                recipes_list.append(recipe)       
            return recipes_list

    def get_recipe(self, recipe_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()       
            cur.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
            tup = cur.fetchone()
            return Recipe(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
    
    def update_recipe_counts(self, recipe_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(user_id) FROM tried WHERE recipe_id = %s", (recipe_id,))
            tried_count = cur.fetchone()[0]
            if tried_count == None:
                tried_count = 0
            cur.execute("SELECT SUM(vote_type) FROM recipe_votes WHERE recipe_id = %s", (recipe_id,))
            like_count = cur.fetchone()[0]
            if like_count == None:
                like_count = 0
            cur.execute("UPDATE recipes SET triedcount = %s, likecount = %s WHERE id = %s", (tried_count, like_count, recipe_id))

    def  get_recipe_ingredients(self, recipe_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT ingredient_id FROM ingredient_mapper")
            ingredient_ids = cur.fetchall()
            ingredients = []
            for ingredient_id in ingredient_ids:
                cur.execute("SELECT ingredient_name FROM ingredients WHERE id = %s", (ingredient_id[0],))
                ingredients.append(cur.fetchone())
            return ingredients
    
    def  get_recipe_tools(self, recipe_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT tool_id FROM tool_mapper")
            tool_ids = cur.fetchall()
            tools = []
            for tool_id in tool_ids:
                cur.execute("SELECT tool_name FROM tools WHERE id = %s", (tool_id[0],))
                tools.append(cur.fetchone())
            return tools

    def check_tried(self, recipe_id, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tried WHERE recipe_id = %s and user_id = %s ", (recipe_id, user_id))
            tup = cur.fetchone()
            if tup:
                return True
            else:
                return False

    def add_tried(self, recipe_id, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO tried (recipe_id, user_id) VALUES (%s, %s)", (recipe_id, user_id))
            conn.commit()
    def remove_tried(self, recipe_id, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM tried WHERE recipe_id = %s AND user_id = %s", (recipe_id, user_id))
            conn.commit()

    def check_recipe_like_dislike(self, recipe_id, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM recipe_votes WHERE recipe_id = %s AND user_id = %s", (recipe_id,user_id))
            tup = cur.fetchone()
            if tup:
                return tup[0] # return 1 if upvote -1 if downvote
            else:
                return 0 # return 0 if vote doesn't exist        

    def vote_recipe(self, recipe_id, user_id, vote_type, prev_vote): # This removes, creates and updates votes all together
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()

            if prev_vote == 0:
                cur.execute("INSERT INTO recipe_votes (vote_type, user_id, recipe_id) VALUES (%s, %s, %s)", (vote_type, user_id, recipe_id))
                conn.commit()
            elif prev_vote == vote_type:
                cur.execute("DELETE FROM recipe_votes WHERE vote_type = %s AND user_id = %s AND recipe_id = %s", (vote_type, user_id, recipe_id))
                conn.commit()
            else:
                cur.execute("UPDATE recipe_votes SET vote_type = %s WHERE user_id = %s AND recipe_id = %s", (vote_type, user_id, recipe_id))
                conn.commit()
    def vote_comment(self, comment_id, user_id, vote_type, prev_vote):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            if prev_vote == 0:
                cur.execute("INSERT INTO comment_votes (vote_type, user_id, comment_id) VALUES (%s, %s, %s)", (vote_type, user_id, comment_id))
                conn.commit()
            elif prev_vote == vote_type:
                cur.execute("DELETE FROM comment_votes WHERE vote_type = %s AND user_id = %s AND comment_id = %s", (vote_type, user_id, comment_id))
                conn.commit()
            else:
                cur.execute("UPDATE comment_votes SET vote_type = %s WHERE user_id = %s AND comment_id = %s", (vote_type, user_id, comment_id ))
                conn.commit()
                
    def check_comment_like_dislike(self, comment_id, user_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM comment_votes WHERE comment_id = %s AND user_id = %s", (comment_id ,user_id))
            tup = cur.fetchone()
            if tup:
                return tup[0] # return 1 if upvote -1 if downvote
            else:
                return 0 # return 0 if vote doesn't exist      

    def update_comment_like_counts(self, comment_id):
        with psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda") as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(vote_type) FROM comment_votes WHERE comment_id = %s ", (comment_id,))        
            like_count = cur.fetchone()[0]
            if like_count== None:
                like_count = 0 
            cur.execute("UPDATE comments SET likecount = %s WHERE id = %s",(like_count, comment_id))          
