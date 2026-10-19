from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.order_history import OrderHistory
from .models.sale import SaleHistory
from .models.inventory import Inventory
from .models.product_reviews import ProductReview
from .models.seller import Seller

from flask import Blueprint

import math

bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address_number = StringField('Street Number', validators=[DataRequired()])
    address_street = StringField('Street', validators=[DataRequired()])
    address_zip = StringField('Zipcode', validators=[DataRequired()])
    starting_balance = StringField('Starting Balance', validators=[DataRequired()])
    submit = SubmitField('Register')

    # def validate_email(self, email):
    #     if User.email_exists(email.data):
    #         raise ValidationError('Already a user with this email.')

class BalanceForm(FlaskForm):
    balance = StringField('Amount', validators=[DataRequired()])
    submit = SubmitField('Register')

    # def validate_email(self, email):
    #     if User.email_exists(email.data):
    #         raise ValidationError('Already a user with this email.')

class SearchForm(FlaskForm):
    account = StringField('Account Number', validators=[DataRequired()])
    submit = SubmitField('Search')

@bp.route('/Profile', methods=['GET', 'POST'])
def profile():
    if current_user.is_authenticated:
        user_id = current_user.id
        user_info = User.get(user_id)

        curpage = request.args.get('curpage', 1, type=int)
        per_page = 10
        order_history, totalpage = OrderHistory.get_by_user_id(user_id, curpage, per_page)
        
        for order in order_history:
            order.has_review = order.prod_review_id is not None
            
        if Seller.is_seller(user_id):
            inventory = Inventory.get_seller_products(user_id, page=1, per_page=5, is_seller=True)
            sale_unfulfilled = SaleHistory.get_unfulfilled(user_id,page=1, per_page=5)
            sale_fulfilled = SaleHistory.get_fulfilled(user_id,page=1, per_page=5)
        else:
            inventory = []
            sale_unfulfilled = []
            sale_fulfilled = []
        form = BalanceForm()
        if form.validate_on_submit():
            action = request.form.get('action')

            if action == 'add':
                if User.edit_balance(user_id, True, form.balance.data) is not None:
                    flash('Balance has been added!')
                else:
                    flash('Error adding balance. Try again!')
            elif action == 'withdraw':
                if User.edit_balance(user_id, False, form.balance.data) is not None:
                    flash('Balance has been withdrawn!')
                else:
                    flash('Error withdrawing balance. Try again!')

            return redirect(url_for('users.profile'))
        
        form_search = SearchForm()
        if form_search.validate_on_submit():
            search_id = form_search.account.data
            if not search_id.isdigit():
                flash('Invalid Account Number.')
                return redirect(url_for('users.profile', user_id=user_id))
            searched_user = User.get(search_id)

            if searched_user is not None:
                return redirect(url_for('users.public_profile', user_id=searched_user.id))
            else:
                flash('User not found.')


        return render_template('profile.html', user = user_info,\
                                order_history = order_history, \
                                inventory = inventory, \
                                sale_unfulfilled=sale_unfulfilled,\
                                sale_fulfilled=sale_fulfilled, \
                                form=form, \
                                curpage=curpage, \
                                totalpage=totalpage, \
                                form_search=form_search)
    else:
        flash('You need to be logged in to view or edit your profile.')
        return redirect(url_for('users.login'))
    
@bp.route('/public/<int:user_id>', methods=['GET', 'POST'])
def public_profile(user_id):
    is_seller = Seller.is_seller(user_id)
    user_info = User.get(user_id)

    if is_seller:
        curpage = request.args.get('curpage', 1, type=int)
        curpage_product = request.args.get('curpage_product', 1, type=int)
        per_page = 10

        user_products = Inventory.get_seller_products(user_id, page=curpage_product, per_page=per_page, is_seller=False)
        user_reviews = ProductReview.get_seller_reviews(user_id, curpage, per_page)
        seller_review_count = ProductReview.get_seller_review_count(user_id)
        totalpage = math.ceil(seller_review_count / per_page)

        seller_product_count = Inventory.get_inventory_count(user_id)
        totalpage_product = math.ceil(seller_product_count / per_page)
    else:
        user_products = []
        user_reviews = []
        curpage = 1
        totalpage = 1
        curpage_product = 1
        totalpage_product = 1

    return render_template('public_user.html',
                           user_info=user_info,
                           user_products=user_products,
                           user_reviews=user_reviews,
                           curpage=curpage,
                           totalpage=totalpage,
                           curpage_product=curpage_product,
                           totalpage_product=totalpage_product)
                    

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            flash("Password don't match!")
            return redirect(url_for('users.register'))
        if User.register(form.email.data,
                         form.password.data,
                         form.address_number.data,
                         form.address_street.data,
                         form.address_zip.data,
                         form.starting_balance.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

class EditProFileForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    email = StringField('Email')
    ship_address_number = StringField('Shipping Address Street Number')
    ship_address_street = StringField('Shipping Address Street')
    ship_address_zip = StringField('Shipping Address Zipcode')
    bill_address_number = StringField('Billing Address Street Number')
    bill_address_street = StringField('Billing Address Street')
    bill_address_zip = StringField('Billing Address Zipcode')
    user_bio = StringField('User Bio')
    old_password = StringField('Old Password')
    new_password = StringField('New Password')
    new_password2 = StringField('New Password')
    submit = SubmitField('Edit')


@bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProFileForm()
    user_id = current_user.id
    user_info = User.get(user_id)
    if form.validate_on_submit():
        if User.edit_info(user_id, 
                        form.ship_address_number.data,
                        form.ship_address_street.data,
                        form.ship_address_zip.data,
                        form.bill_address_number.data,
                        form.bill_address_street.data,
                        form.bill_address_zip.data,
                        form.user_bio.data,
                        form.firstname.data,
                        form.lastname.data,
                        form.old_password.data,
                        form.new_password.data,
                        form.new_password2.data,
                        form.email.data) is not None:
            flash('Profile has been edited!')
            return redirect(url_for('users.login'))
        else:
            flash('Error! Profile has not been edited!')
    return render_template('edit_profile.html', title='Edit Profile', user_info = user_info, form=form)

@bp.route('/convert-to-seller', methods=['POST'])
def convert_to_seller():
    user_id = current_user.id
    if User.convert_to_seller(user_id):
        flash('Successfully converted to seller!')
    else:
        flash('Error! Could not convert to seller.')
    return redirect(url_for('users.login'))