from flask import Blueprint, abort, jsonify, request, send_from_directory
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from media import ITEM_UPLOAD_DIR, save_upload_image

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/items", methods=["POST"])
def upload_item_images():
    try:
        files = request.files.getlist("files")
        if not files:
            single = request.files.get("file")
            if single:
                files = [single]

        if not files:
            return jsonify({"error": "No files uploaded"}), 400
        if len(files) > 9:
            return jsonify({"error": "Maximum 9 images allowed"}), 400

        paths = []
        for f in files:
            if not f or not getattr(f, "filename", ""):
                continue
            try:
                paths.append(save_upload_image(f))
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        if not paths:
            return jsonify({"error": "No valid files uploaded"}), 400

        return jsonify({"paths": paths}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@upload_bp.route("/items/<path:filename>", methods=["GET"])
def get_item_image(filename: str):
    if not filename:
        abort(404)
    return send_from_directory(ITEM_UPLOAD_DIR, filename)
