from flask import Flask, render_template
from datetime import datetime
import view

from database import Database
from recipe import Recipe
from comment import Comment
from discussion import Discussion

def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/recipes", view_func=view.recipes_page,  methods = ["GET", "POST"])
    app.add_url_rule("/recipes/<int:recipe_key>", view_func = view.recipe_page)
    app.add_url_rule("/discussions", view_func= view.discussions_page)
    app.add_url_rule("/discussion/<int:discussion_key>", view_func = view.discussion_page)

    db = Database()
    db.add_recipe(Recipe("Shakshuka", "Fırını 180 derecede ısıt, patatesleri doğrayıp fırın tepsisine diz, 45dk fırına pişir.", "tatlı patates"))
    db.add_recipe(Recipe("Humus", "yagla magla", "nohut"))

    comment1 = Comment("Arda", 15, "Ovvvvvvvv yeaaaaaaa")
    comment2 = Comment("Ismail", -1, "lorem ipsum falanium filanium")
    comment_list = [comment1, comment2]
    first_diss = Discussion("Idil", "Bence yemekler cok lezzetli", 12, comment_list, "Yasasin yemekler")
    db.add_discussion(first_diss)
    comment_list_empty = []
    second_diss = Discussion("Selami", "Yemekler çok tuzlu", 0, comment_list_empty, "Lanet olsun yemekler")
    db.add_discussion(second_diss)
    app.config["db"] = db
    print(db.discussions)
    print("HELLO WORLD")
    return app



if __name__ == "__main__":
    app = create_app()
    app.debug = True
    app.run(host="0.0.0.0", port=5001, debug=True)