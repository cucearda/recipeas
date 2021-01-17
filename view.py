from flask import Flask, render_template, current_app, request, redirect, url_for, flash
from recipe import Recipe
from post import Post
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
    else:
        recipe_ids = request.form.getlist("recipe_ids")
        for recipe_id in recipe_ids:
            db.delete_recipe(recipe_id)
            recipes = db.get_recipes()
    return render_template("recipes.html", recipes=recipes)  

def recipe_page(recipe_id):
    db = current_app.config["db"]
    recipe = db.get_recipe(recipe_id)
    tried = db.check_tried(recipe_id, current_user.userid)
    tools = db.get_recipe_tools(recipe_id)
    ingredients = db.get_recipe_ingredients(recipe_id)
    prev_vote = db.check_recipe_like_dislike(recipe_id, current_user.userid)
    return render_template("recipe.html", recipe = recipe, tried=tried, tools = tools, ingredients = ingredients, prev_vote = prev_vote)

def posts_page(): # commenterların karmasını güncelleme şeklini değiştir !
    db = current_app.config["db"]
    if request.method == "GET":
        posts = db.get_posts()
        return render_template("forum_posts.html", posts = posts)
    
    else:
        post_ids = request.form.getlist("post_ids")
        for post_id in post_ids:
            commented_user_ids = []
            for comment in db.get_post_comments(post_id):
                commented_user_ids.append(comment.user.userid)

            db.update_post_owner(post_id) # update post owners karma (before deletion so we can access like count)
            db.delete_post(post_id)
            for user_id in commented_user_ids: # update commenters karma after deletion
                db.update_user_karma(user_id)
            
        posts = db.get_posts()
        return render_template("forum_posts.html", posts = posts)



def post_page(post_id):
    if request.method == "GET":
        db = current_app.config["db"]
        post = db.get_post(post_id)
        comments = db.get_post_comments(post_id)
        return render_template("forum_post.html", post = post, comments = comments)
    else:
        db = current_app.config["db"]
        comment = request.form["comment"]
        db.create_comment(post_id, comment, current_user.userid)
        db.update_post_commentcounts(post_id)
        return redirect(url_for('post_page', post_id = post_id))


@login_required
def create_post_page():
    if request.method == "GET":
        return render_template("create_post.html")
    else:
        db = current_app.config["db"]
        title = request.form["title"]
        content = request.form["content"]
        user_id = current_user.userid
        date = datetime.now()
        db.create_post(content, title, user_id, date)
        return redirect(url_for('home_page'))

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
        if(db.add_user(username, hashed, nickname, karma, date, False)):
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
    if vote_type  == 2: # we can't send negative integers through url so we send 2 and translate it to -1
        vote_type = -1 
    prev_vote = db.check_recipe_like_dislike(recipe_id, current_user.userid)
    db.vote_recipe(recipe_id, current_user.userid, vote_type, prev_vote)
    db.update_recipe_counts(recipe_id)
    flash("Vote registered")
    return redirect(url_for('recipe_page', recipe_id = recipe_id))
    
def vote_post_page(post_id, vote_type):
    db = current_app.config["db"]
    if vote_type == 2:
        vote_type = -1
    
    prev_vote = db.check_post_like_dislike(post_id, current_user.userid)
    db.vote_post(post_id, current_user.userid, vote_type, prev_vote)
    db.update_post_like_counts(post_id)
    flash("Vote registered")
    return redirect(url_for('post_page', post_id= post_id))

def vote_comment_page(post_id, comment_id, vote_type):
    db = current_app.config["db"]
    if vote_type == 2:
        vote_type = -1

    prev_vote = db.check_comment_like_dislike(comment_id, current_user.userid)
    db.vote_comment(comment_id, current_user.userid, vote_type, prev_vote)
    db.update_comment_like_counts(comment_id)
    flash("Vote registered")
    return redirect(url_for('post_page', post_id = post_id))

def search_recipe_page():
    db = current_app.config["db"]
    if request.method == "GET":
        ingredients = db.get_ingredients()
        return render_template("search_recipe.html", ingredients = ingredients)
    else:
        ingredient_ids = request.form.getlist('ingredient_ids')
        if not ingredient_ids:
            flash("Select some ingredients first!")
            return redirect(url_for('search_recipe_page', ingredients = db.get_ingredients()))
        else:
            recipes = []
            recipe_ids = db.get_recipe_ids_by_ingredients(ingredient_ids)
            for recipe_id in recipe_ids:
                recipe = db.get_recipe(recipe_id)
                recipes.append(recipe)
            return render_template("recipes.html", recipes=recipes)  

def top_recipes_page():
    db = current_app.config["db"]
    if request.method == "GET":
        recipes = db.get_top_recipes()
    else:
        recipe_ids = request.form.getlist("recipe_ids")
        for recipe_id in recipe_ids:
            db.delete_recipe(recipe_id)
            recipes = db.get_top_recipes()
    return render_template("recipes.html", recipes=recipes)  

def user_rankings_page():
    if request.method == "GET":
        db = current_app.config["db"]
        users = db.get_users()
    
        users_augmented = [ (user, db.get_user_post_counts(user.userid), db.get_user_recipe_counts(user.userid)) for user in users ]

        return render_template("users_rankings.html", users_augmented=users_augmented)
    else:
        db = current_app.config["db"]
        user_ids = request.form.getlist("user_ids")
        for user_id in user_ids:
            
            voted_comments = db.get_voted_comments(user_id) # returns ids not objects.
            voted_posts = db.get_voted_posts(user_id)
            recipes_to_update = db.get_altered_recipes(user_id) #  returns recipe_ids of both tried and voted recipes
            
            # which users karmas should be updated, are calculated before deletion.
            voted_comment_owners = []
            voted_recipe_owners = []
            voted_post_owners = []
             
            for comment_id in voted_comments:
                voted_comment_owners.append(db.get_comment_owner_id(comment_id))
            for recipe_id in recipes_to_update:
                voted_recipe_owners.append(db.get_recipe_owner_id(recipe_id))
            for post_id in voted_posts:
                voted_post_owners.append(db.get_post_owner_id(post_id))

            comment_under_post_owners = db.get_comment_owners_of_users_posts(user_id) # if a user commented under any post of user to be deleted, commenters karma may need to be updated

            users_to_update = list(set(voted_comment_owners).union(set(voted_recipe_owners), set(voted_post_owners), set(comment_under_post_owners))) # we are selecting comment owners etc. from a list of comment ids, so doing the selection and  union in one query became too complicated

            # deletion of user, it cascades and deletes all votes, posts and comments of user.
            db.delete_user(user_id)

            for comment in voted_comments: # update the like and tried counts of the objects user has altered.
                db.update_comment_like_counts(comment)
            for post in voted_posts:
                db.update_post_like_counts(post)
                db.update_post_commentcounts(post)
            for recipe in recipes_to_update:
                db.update_recipe_counts(recipe)

            for user_id in users_to_update:
                db.update_user_karma(user_id)

        return  redirect(url_for('user_rankings_page'))

def delete_comment_page(post_id, comment_id):
    db = current_app.config["db"]
    db.delete_comment(comment_id) # both deletes comment and updates user karma
    return redirect(url_for('post_page', post_id = post_id))
