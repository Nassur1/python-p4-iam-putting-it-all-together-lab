from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

# ---------------- Root ----------------
@app.route("/")
def home():
    return {"message": "Welcome to the Recipes API!"}, 200

# ---------------- Signup ----------------
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"errors": ["Username and password required"]}, 422

        user = User(
            username=username,
            bio=data.get("bio"),
            image_url=data.get("image_url")
        )
        user.password = password

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already exists"]}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201

# ---------------- Check Session ----------------
class CheckSession(Resource):
    def get(self):
        uid = session.get("user_id")
        if not uid:
            return {"errors": ["Not logged in"]}, 401

        user = User.query.get(uid)
        return user.to_dict(), 200

# ---------------- Login ----------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()
        if not user or not user.authenticate(data.get("password")):
            return {"errors": ["Invalid username or password"]}, 401

        session["user_id"] = user.id
        return user.to_dict(), 200

# ---------------- Logout ----------------
class Logout(Resource):
    def delete(self):
        # More explicit check
        user_id = session.get("user_id")
        
        if user_id is None:
            return "", 401
        
        session.pop("user_id", None)
        return "", 204



# ---------------- Recipes ----------------
class RecipeIndex(Resource):
    def get(self):
        uid = session.get("user_id")
        if not uid:
            return {"errors": ["Unauthorized"]}, 401

        recipes = Recipe.query.filter_by(user_id=uid).all()
        return [r.to_dict() for r in recipes], 200

    def post(self):
        uid = session.get("user_id")
        if not uid:
            return {"errors": ["Unauthorized"]}, 401

        data = request.get_json()
        required = ["title", "instructions", "minutes_to_complete"]
        if not all(k in data for k in required):
            return {"errors": ["Missing required fields"]}, 422

        try:
            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=uid
            )
            db.session.add(recipe)
            db.session.commit()
        except:
            db.session.rollback()
            return {"errors": ["Invalid data"]}, 422

        return recipe.to_dict(), 201

# ---------------- Register Resources ----------------
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
