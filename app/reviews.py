from flask import jsonify, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
import datetime
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import HiddenField, TextAreaField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from app.models.order_history import OrderHistory
from app.models.product_reviews import ProductReview
from app.models.user_reviews import UserReview
bp = Blueprint('reviews', __name__)


# Get all product reviews by the current user
@bp.route('/productreviews', methods=['GET'])
def get_user_reviews():
    if not current_user.is_authenticated:
        return jsonify({}), 404

    sort_order = request.args.get('sort', 'rating_desc')

    user_id = current_user.id
    reviews = ProductReview.get_all_by_user(person_reviewing_id=user_id, sort_order=sort_order)
    return render_template('reviews.html', reviews=reviews, sort_order=sort_order)

# Get all user reviews by the current user
@bp.route('/userreviews', methods=['GET'])
def get_user_user_reviews():
    if not current_user.is_authenticated:
        return jsonify({}), 404

    sort_order = request.args.get('sort', 'rating_desc')

    user_id = current_user.id
    reviews = UserReview.get_all_by_user(person_reviewing_id=user_id, sort_order=sort_order)
    return render_template('user_reviews.html', reviews=reviews, sort_order=sort_order)


# Get recent reviews by the current user
@bp.route('/productreviews/recent', methods=['GET'])
def get_recent_reviews():
    if not current_user.is_authenticated:
        return jsonify({}), 404
    user_id = current_user.id
    reviews = ProductReview.get_recent_by_user(person_reviewing_id=user_id)
    return render_template('reviews.html', reviews=reviews)

class ReviewForm(FlaskForm):
    review_rating = DecimalField('Rating', validators=[DataRequired(), NumberRange(min=0.0, max=5.0)])
    review_description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

# Add a review for a product
@bp.route('/productreviews/add/<int:order_id>', methods=['GET', 'POST'])
@login_required
def add_review(order_id):
    form = ReviewForm()
    if form.validate_on_submit():
        print (form.review_rating.data)
        if ProductReview.add_review(order_id, form.review_rating.data, form.review_description.data):
            flash('Your review has been added successfully!', 'success')
            return redirect(url_for('users.profile'))
        else:
            flash('Failed to add review.', 'error')
    return render_template('add_review.html', form=form, order_id=order_id)