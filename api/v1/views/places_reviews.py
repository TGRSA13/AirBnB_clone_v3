#!/usr/bin/python3
"""Places review"""
from api.v1.views import app_views
from flask import jsonify, abort, make_response, request
from flasgger.utils import swag_from
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/review/get_reviews.yml', methods=['GET'])
def get_reviews(place_id):
    """get all review objects"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    review_list = []
    for review in place.reviews:
        review_list.append(review.to_dict())

    return jsonify(review_list)


@app_views.route('/reviews/<review_id>', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/review/get_review.yml', methods=['GET'])
def get_review(review_id):
    """Get a particular review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/review/delete_reviews.yml', methods=['DELETE'])
def delete_review(review_id):
    """Delete Review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    storage.delete(review)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/review/post_review.yml', methods=['POST'])
def post_review(place_id):
    """Create a new review"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    request_data = request.get_json()
    if not request_data:
        abort(400, description='Not a JSON')

    if 'user_id' not in request_data:
        abort(400, description='Missing user_id')

    user = storage.get(User, request_data['user_id'])
    if not user:
        abort(404)

    if 'text' not in request_data:
        abort(400, description='Missing text')

    request_data['place_id'] = place_id
    review = Place(**request_data)
    review.save()

    return make_response(jsonify(review.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
@swag_from('documentation/review/put_reviews.yml', methods=['PUT'])
def put_review(review_id):
    """Update a review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    request_data = request.get_json()
    if not request_data:
        abort(400, description='Not a JSON')

    ignore_keys = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    for key, value in request_data.items():
        if key not in ignore_keys:
            setattr(review, key, value)
    storage.save()

    return make_response(jsonify(review.to_dict()), 200)
