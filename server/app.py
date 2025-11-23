from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

# ------------------------ Root Route ------------------------
@app.route("/")
def home():
    return {"message": "Welcome to the Recipes API!"}, 200


# ------------------------ Signup ------------------------
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        bio = data.get("bio")
        image_url = data.get("image_url")

        if not username or not password:
            return {"errors": ["Username and password required"]}, 422

        user = User(username=username, bio=bio, image_url=image_url)
        user.password = password

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already exists"]}, 422

        session['user_id'] = user.id

        return {"id": user.id, "username": user.username, "bio": user.bio, "image_url": user.image_url}, 201


# ------------------------ Check Session ------------------------
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"errors": ["Not logged in"]}, 401

        user = User.query.get(user_id)
        if not user:
            return {"errors": ["User not found"]}, 401

        return {"id": user.id, "username": user.username, "bio": user.bio, "image_url": user.image_url}, 200


# ------------------------ Login ------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {"errors": ["Invalid username or password"]}, 401

        session['user_id'] = user.id
        return {"id": user.id, "username": user.username, "bio": user.bio, "image_url": user.image_url}, 200


# ------------------------ Logout ------------------------
class Logout(Resource):
    def delete(self):
        if "user_id" not in session:
            return {"errors": ["Not logged in"]}, 401
        session.pop("user_id")
        return "", 204


# ------------------------ Recipes ------------------------
class RecipeIndex(Resource):
    def get(self):
        if "user_id" not in session:
            return {"errors": ["Unauthorized"]}, 401

        recipes = Recipe.query.all()
        result = []
        for recipe in recipes:
            result.append({
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "bio": recipe.user.bio,
                    "image_url": recipe.user.image_url
                }
            })
        return result, 200

    def post(self):
        if "user_id" not in session:
            return {"errors": ["Unauthorized"]}, 401

        data = request.get_json()
        title = data.get("title")
        instructions = data.get("instructions")
        minutes = data.get("minutes_to_complete")

        if not title or not instructions or not minutes:
            return {"errors": ["All fields required"]}, 422

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes,
            user_id=session["user_id"]
        )

        try:
            db.session.add(recipe)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

        return {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {
                "id": recipe.user.id,
                "username": recipe.user.username,
                "bio": recipe.user.bio,
                "image_url": recipe.user.image_url
            }
        }, 201


# ------------------------ Register Resources ------------------------
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


# ------------------------ Run App ------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
