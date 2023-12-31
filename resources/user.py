from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity
from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @jwt_required()  # Comentar la primera vez que creas un usuario
    @blp.arguments(UserSchema)
    def post(self, user_data):
        jwt = get_jwt()    # Comentar la primera vez que creas un usuario
        if not jwt.get("is_admin"):    # Comentar la primera vez que creas un usuario
            abort(401, message="Admin privilege required.")    # Comentar la primera vez que creas un usuario

        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(username=user_data["username"], password=pbkdf2_sha256.hash(user_data["password"]),)

        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    @blp.arguments(UserSchema)
    def put(self, user_data, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

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

    @jwt_required()
    def delete(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200