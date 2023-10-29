from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(username=user_data["username"], password=pbkdf2_sha256.hash(user_data["password"]),)

        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.arguments(UserSchema)
    def put(self, user_data, user_id):
        user = UserModel.query.get_or_404(user_id)

        if 'username' not in user_data:
            return {'message': 'No se proporcionó un nombre de usuario válido.'}, 400

        if 'password' not in user_data:
            return {'message': 'No se proporcionó una contraseña válida.'}, 400

        if UserModel.query.filter(UserModel.username == user_data['username'], UserModel.id != user_id).first():
            return {'message': 'Ya existe un usuario con ese nombre.'}, 409

        user.username = user_data['username']
        user.password = pbkdf2_sha256.hash(user_data['password'])
        db.session.commit()

        return {'message': 'Usuario actualizado correctamente.'}, 200

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200

