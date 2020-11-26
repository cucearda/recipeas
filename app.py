from flask import Flask, render_template
from datetime import datetime
import view

from database import Database
from recipe import Recipe


def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", view_func=view.home_page)
    app.add_url_rule("/recipes", view_func=view.recipes_page,  methods = ["GET", "POST"])
    app.add_url_rule("/recipes/<int:recipe_key>", view_func = view.recipe_page)

    db = Database()
    db.add_recipe(Recipe("Shakshuka", "kizart mizart", "patates"))
    db.add_recipe(Recipe("Humus", "yagla magla", "nohut"))
    app.config["db"] = db
    return app



if __name__ == "__main__":
    app = create_app()
    app.debug = True
    app.run(host="0.0.0.0", port=8080, debug=True)