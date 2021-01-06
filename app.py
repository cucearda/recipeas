from flask import Flask, render_template
from datetime import datetime
import view
import psycopg2
from database import Database
from recipe import Recipe
from comment import Comment
from discussion import Discussion
from ingredient import Ingredient
import user
from flask_login import LoginManager


def create_app():
    conn = psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda")
    cur = conn.cursor()
    lm = LoginManager()

    @lm.user_loader
    def load_user(username):
        return user.get_user(username)

    app = Flask(__name__)
    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/recipes", view_func=view.recipes_page,  methods = ["GET", "POST"])
    app.add_url_rule("/recipes/<int:recipe_key>", view_func = view.recipe_page)
    app.add_url_rule("/discussions", view_func= view.discussions_page)
    app.add_url_rule("/discussion/<int:discussion_key>", view_func = view.discussion_page)
    app.add_url_rule("/create_post", view_func= view.create_post_page, methods =["GET", "POST"])
    app.add_url_rule("/create_recipe", view_func = view.create_recipe_page, methods =["GET", "POST"])
    app.add_url_rule("/signup", view_func=view.signup_page, methods = ["POST","GET"])
    app.add_url_rule("/login", view_func=view.login_page, methods=["POST", "GET"])
    app.add_url_rule("/logout", view_func=view.logout_page)



    db = Database()
    db.add_recipe(Recipe("Shakshuka", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure", "Patates"))
    db.add_recipe(Recipe("Humus", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure", "Nohut"))
    db.add_ingredient(Ingredient("Nohut"))
    db.add_ingredient(Ingredient("Pirinc"))
    db.add_ingredient(Ingredient("Bezelye"))

    comment1 = Comment("Arda", 15, "lorem ipsum sit amet")
    comment2 = Comment("Ismail", -1, "lorem ipsum sit amet")
    comment_list = [comment1, comment2]
    first_diss = Discussion("John Doe", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure", 12, comment_list, "Lorem ipsum dolor")
    db.add_discussion(first_diss)
    comment_list_empty = []
    second_diss = Discussion("Jane Doe", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure", 0, comment_list_empty, "Excepteur sint occaecat cupidatat")
    db.add_discussion(second_diss)
    app.config["db"] = db

    lm.init_app(app)
    lm.login_view = "login_page"


    cur.close()
    conn.close()
    
    return app



if __name__ == "__main__":
    app = create_app()
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host="0.0.0.0", port=8086, debug=True)