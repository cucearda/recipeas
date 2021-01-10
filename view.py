from flask import Flask, render_template, current_app, request, redirect, url_for, flash
from recipe import Recipe
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as hasher
import user
import psycopg2
from flask_login import login_user, logout_user, login_required, current_user

def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)

def recipes_page():
    db = current_app.config["db"]
    if request.method == "GET":
        recipes = db.get_recipes()
    return render_template("recipes.html", recipes=recipes)  

def recipe_page(recipe_id):
    db = current_app.config["db"]
    recipe = db.get_recipe(recipe_id)
    tried = db.check_tried(recipe_id, current_user.userid)
    tools = db.get_recipe_tools(recipe_id)
    ingredients = db.get_recipe_ingredients(recipe_id)
    prev_vote = db.check_like_dislike(recipe_id, current_user.userid)
    return render_template("recipe.html", recipe = recipe, tried=tried, tools = tools, ingredients = ingredients, prev_vote = prev_vote)

def discussions_page():
    db = current_app.config["db"]
    if request.method == "GET":
        discussions = db.get_discussions()
    return render_template("discussions.html", discussions = sorted(discussions))


def discussion_page(discussion_key):
    db = current_app.config["db"]
    discussion = db.get_discussion(discussion_key)
    return render_template("discussion.html", discussion = discussion)

@login_required
def create_post_page():
    if request.method == "GET":
        return render_template("create_post.html")
    else:
        title = request.form["title"]
        content = request.form["content"]
        print(title)
        print(content)
        return render_template("home.html")

@login_required
def create_recipe_page():
    db = current_app.config["db"]
    ingredients = db.get_ingredients()
    tools = db.get_tools()
    if request.method == "GET":
        return render_template("create_recipe.html", ingredients = ingredients, tools = tools)
    else:
        ingredient_ids = request.form.getlist('ingredient_ids')
        tool_ids = request.form.getlist('tool_ids')
        body = request.form["content"]
        title = request.form["title"]
        if not tool_ids or not ingredient_ids:
            flash("Choose some tools and ingredients!")
            return redirect(url_for('create_recipe_page'))
        db.create_recipe(body, title, ingredient_ids, tool_ids, current_user.userid)
        return render_template("home.html")

def signup_page():
    db = current_app.config["db"]
    if request.method == "GET":
        return render_template("signup_page.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        nickname = request.form["nickname"]
        hashed = hasher.hash(password)
        karma = 0
        date = datetime.now()
        if(db.add_user(username, hashed, nickname, karma, date)):
            flash("Registired")
            return redirect(url_for('login_page'))
        else:
            flash("Username already exists.")
            return render_template("signup_page.html")


def login_page():

    if request.method == "GET":
        return render_template("login.html")
    else:
        entered_username = request.form["username"]
        entered_password = request.form["password"]
        entered_user = user.get_user(entered_username)
        if entered_user != None:
            if hasher.verify(entered_password, entered_user.password):
                login_user(entered_user)
                flash("Welcome " + entered_user.username)
                return render_template("home.html")
            else:
                flash("Wrong password")
                return render_template("login.html")
        else:
            flash("Wrong user name")
            return render_template("login.html")

def logout_page():
    logout_user()
    flash("Goodbye")
    return redirect(url_for("home_page"))

def create_ingredient_page():
    if request.method == "GET":
        return render_template("create_ingredient.html")
    
    else:
        db = current_app.config["db"]
        entered_ingredient = request.form["ingredient"]
        if(db.add_ingredient(entered_ingredient)):
            flash("Ingredient added to database")
        else:
            flash("Ingredient already exists")
        return render_template("create_ingredient.html")

def create_tool_page():
    if request.method == "GET":
        return render_template("create_tool.html")

    else:
        db=current_app.config["db"]
        entered_tool = request.form["tool"]
        if(db.add_tool(entered_tool)):
            flash("Tool added to database")
        else:
            flash("Tool already exists")
        return render_template("create_tool.html")

def tried_page(recipe_id):
    db = current_app.config["db"]
    if db.check_tried(recipe_id, current_user.userid):
        db.remove_tried(recipe_id, current_user.userid)
    else:
        db.add_tried(recipe_id, current_user.userid)
    db.update_recipe_counts(recipe_id)
    return redirect(url_for('recipe_page', recipe_id = recipe_id))

def vote_recipe_page(recipe_id, vote_type):
    db = current_app.config["db"]
    if vote_type  == 2:
        vote_type = -1
    prev_vote = db.check_like_dislike(recipe_id, current_user.userid)
    db.vote_recipe(recipe_id, current_user.userid, vote_type, prev_vote)
    db.update_recipe_counts(recipe_id)
    flash("Vote registered")
    return redirect(url_for('recipe_page', recipe_id = recipe_id))
    
