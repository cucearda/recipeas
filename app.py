from flask import Flask, render_template
from datetime import datetime
import view
import psycopg2
from database import Database
from recipe import Recipe
from comment import Comment
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
    app.add_url_rule("/recipes/<int:recipe_id>", view_func = view.recipe_page)
    app.add_url_rule("/posts", view_func= view.posts_page)
    app.add_url_rule("/post/<int:post_id>", view_func = view.post_page, methods = ["GET", "POST"])
    app.add_url_rule("/create_post", view_func= view.create_post_page, methods =["GET", "POST"])
    app.add_url_rule("/create_recipe", view_func = view.create_recipe_page, methods =["GET", "POST"])
    app.add_url_rule("/signup", view_func=view.signup_page, methods = ["POST","GET"])
    app.add_url_rule("/login", view_func=view.login_page, methods=["POST", "GET"])
    app.add_url_rule("/logout", view_func=view.logout_page)
    app.add_url_rule("/create_ingredient", view_func=view.create_ingredient_page, methods=["POST", "GET"])
    app.add_url_rule("/create_tool", view_func= view.create_tool_page, methods = ["POST", "GET"])
    app.add_url_rule("/tried/<int:recipe_id>", view_func = view.tried_page)
    app.add_url_rule("/recipes/<int:recipe_id>/<int:vote_type>", view_func = view.vote_recipe_page)
   
    db = Database()
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
    app.run(host="0.0.0.0", port=8080, debug=True)