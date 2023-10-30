from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):  # Recupera todas las etiquetas asociadas a una tienda específica.
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()

    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):  # Crea una nueva etiqueta y la asocia a una tienda específica, si no existe ya una etiqueta con el mismo nombre en esa tienda.
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="A tag with that name already exists in that store.")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e),)

        return tag


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @jwt_required()
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):  # Asocia una etiqueta existente a un elemento existente en la base de datos.
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag

    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def put(self, tag_data, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag not in item.tags:
            item.tags.append(tag)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag

    @jwt_required()
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):  # Elimina la asociación entre un elemento y una etiqueta específica.
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag in item.tags:
            item.tags.remove(tag)

            try:
                db.session.add(item)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="An error occurred while inserting the tag.")

            return {"message": "Item removed from tag", "item": item, "tag": tag}
        else:
            abort(404, message="The provided tag is not associated with the item.")


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema)
    def get(self, tag_id):  # Recupera información sobre una etiqueta específica.
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def put(self, tag_data, tag_id):  # Actualiza el nombre de una etiqueta específica.
        tag = TagModel.query.filter_by(id=tag_id).first_or_404()

        tag.name = tag_data.get("name", tag.name)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag

    @jwt_required()
    @blp.response(202, description="Deletes a tag if no item is tagged with it.", example={"message": "Tag deleted."},)
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.",)
    def delete(self, tag_id):  # Elimina una etiqueta, pero solo si no está asociada a ningún elemento. En caso de que esté asociada a algún elemento, devuelve un error
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(400, message="Could not delete tag. Make sure tag is not associated with any items, then try again.",)


