from flask import Flask, render_template, current_app, request, redirect, url_for
from recipe import Recipe
from datetime import datetime

def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)

def recipes_page():
    db = current_app.config["db"]
    if request.method == "GET":
        recipes = db.get_recipes()
    return render_template("recipes.html", recipes=sorted(recipes))  

def recipe_page(recipe_key):
    db = current_app.config["db"]
    recipe = db.get_recipe(recipe_key)
    return render_template("recipe.html", recipe = recipe)