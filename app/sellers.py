from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user
from .models.seller import Seller
from .models.inventory import Inventory
from .models.product_reviews import ProductReview
from .models.sale import SaleHistory
from .models.user import User
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, FloatField
from wtforms.validators import ValidationError, DataRequired, EqualTo, NumberRange, InputRequired
from flask_login import current_user, login_required
from flask import current_app as app
import math
from werkzeug.utils import secure_filename
import os
import io
import base64
import matplotlib.pyplot as plt


from flask import Blueprint
bp = Blueprint('sellers', __name__)


@bp.route('/Sellers', methods=['POST', 'GET'])
def all_sellers():
    page = request.args.get('page', 1, type=int)
    sort, order = request.args.get('seller_sort', "name_asc", type=str).split('_')
    rating = request.args.get('rating_filter', 0, type=int)
    per_page = 15
    selected_state = request.args.get('selected_state', "All", type=str)
    sellers = Seller.get_all(sort, order, rating, selected_state, page=page,per_page=per_page)
    num_sellers = Seller.get_count(rating=rating, selected_state=selected_state)
    total_pages = math.ceil(num_sellers / per_page)
    all_states = Seller.all_states()
    
    return render_template('sellers_page.html', sellers=sellers,\
                                                current_page=page, total_pages=total_pages,\
                                                rating_filter=rating, seller_sort=request.args.get('seller_sort', "name_asc", type=str),\
                                                all_states = all_states, state_filter=selected_state)
class SearchForm(FlaskForm):
    product_id = IntegerField('Filter by top k items', validators=[DataRequired()])
    submit = SubmitField('Search')

@bp.route('/Sellers/<int:seller_id>')
def seller_items(seller_id):
    is_seller = Seller.is_seller(seller_id)
    prod_page = request.args.get('prod_page', 1, type=int)
    review_page = request.args.get('review_page', 1, type=int)
    per_page = 10
    if not is_seller:
        flash('Invalid Seller ID!')
        return redirect(url_for('sellers.all_sellers'))
    seller_products =Inventory.get_seller_products(seller_id, page=prod_page, per_page=per_page)
    seller_product_count = Inventory.get_inventory_count(seller_id)
    seller_total_pages = math.ceil(seller_product_count / per_page)
    seller_info = User.get(seller_id)
    seller_reviews = ProductReview.get_seller_reviews(seller_id,page=review_page,per_page=per_page)
    seller_review_count = ProductReview.get_seller_review_count(seller_id)
    review_total_pages = math.ceil(seller_review_count / per_page)
    form = SearchForm()
    categories = app.db.execute('''SELECT cat_key, cat_name FROM Product_Category ORDER BY cat_name''')
    return render_template('inventory.html',\
                            seller_info = seller_info,\
                            seller_products=seller_products,\
                            seller_current_page=prod_page, seller_total_pages=seller_total_pages,\
                            review_current_page=review_page, review_total_pages=review_total_pages,\
                            seller_reviews=seller_reviews,\
                            categories=categories,\
                            form = form)

@bp.route('/<int:seller_id>/Inventory',methods=['GET'])
@login_required
def seller_inventory(seller_id):
    if current_user.id == seller_id:
        is_seller = Seller.is_seller(seller_id)
        if not is_seller:
            redirect(url_for('users.profile'))
        page = request.args.get('page', 1, type=int)
        per_page = 15
        valid = True
        prod_name = request.args.get('searchInput')
        product_names = ["Lamball", "Cattiva", "Chikipi", "Lifmunk", "Foxparks", "Fuack", "Sparkit", "Tanzee", "Rooby", "Pengullet", 
                            "Penking","Jolthog", "Jolthog Cryst", "Gumoss", "Vixy", "Hoocrates", "Teafant", "Depresso", "Cremis", "Daedream", "Rushoar", 
                            "Nox", "Fuddler", "Killamari", "Mau", "Mau Cryst", "Celaray", "Direhowl", "Tocotoco", "Flopie", "Mozzarina", "Bristla", "Gobfin", "Gobfin Ignis",
                            "Hangyu", "Hangyu Cryst", "Mossanda", "Woolipop", "Caprity", "Melpaca", "Eikthyrdeer", "Eikthyrdeer Terra", "Nitewing", "Ribbuny", "Incineram", "Cinnamoth", "Arsox",
                            "Dumud", "Cawgnito", "Leezpunk", "Loupmoon", "Galeclaw", "Robinquill", "Robinquill Terra", "Gorirat", "Beegarde", "Elizabee", "Grintale", "Swee",
                            "Sweepa", "Chillet", "Univolt", "Pyrin", "Pyrin Noct", "Reindrix", "Rayhound", "Kitsun", "Dazzi", "Lunaris", "Dinossom",
                            "Surfent", "Maraith", "Digtoise", "Tombat", "Lovander", "Flambelle", "Vanwyrm", "Vanwyrm Cryst", "Bushi", "Beakon", "Ragnahawk", "Katress", 
                            "Wixen", "Verdash", "Vaelet", "Sibelyx", "Elphidran", "Kelpsea", "Kelpsea Ignis", "Azurobe", "Cryolinx", "Blazehowl", "Relaxaurus", "Broncherry",
                            "Petallia", "Reptyro", "Reptyro Cryst", "Kingpaca", "Kingpaca Cryst", "Mammorest", "Mammorest Cryst", "Wumpo", "Wumpo Botan", "Warsect", "Fenglope", "Felbat", "Quivern", "Blazamut", "Blazehowl Noct", "Helzephyr", "Astegon",
                            "Menasting", "Anubis", "Jormuntide", "Jormuntide Ignis", "Suzaku", "Grizzbolt", "Lyleen", "Lyleen Noct", "Faleris", "Orserk", "Shadowbeak", "Paladius", "Necromus",
                            "Frostallion", "Jetragon", "Bellanoir"
                        ]
        top_products = SaleHistory.get_top_products(seller_id)
        sort, order = request.args.get('sort_by', "pname_asc", type=str).split('_')
        if not prod_name:
            valid = False
        elif not prod_name.replace(" ", "").isalpha():
            valid = False
            flash("Invalid input! Product names are letters only!")
        elif prod_name not in product_names:
            render_template('seller_inventory.html', seller_product=[], 
                           current_page=1, total_pages=1, seller_id=seller_id, top_products=top_products)
        if valid:
            seller_product = Inventory.get_seller_products(seller_id, sort=sort, order=order,product_name=prod_name.strip(), page=page, per_page=per_page, is_seller=is_seller)
            total_pages = 1
        else:
            seller_product = Inventory.get_seller_products(seller_id, sort=sort, order=order, page=page, per_page=per_page, is_seller=is_seller)
            inventory_count = Inventory.get_inventory_count(seller_id, is_seller=is_seller)
            total_pages = math.ceil(inventory_count / per_page)
        return render_template('seller_inventory.html', seller_product=seller_product, 
                           current_page=page, total_pages=total_pages, seller_id=seller_id, top_products=top_products)
    else:
        redirect(url_for('index.index'))

@bp.route('/<int:seller_id>/Fulfill', methods=['GET', 'POST'])
@login_required
def order_fulfill(seller_id):
    if current_user.id == seller_id:
        is_seller = Seller.is_seller(seller_id)
        if not is_seller:
            redirect(url_for('users.profile'))
        if request.method == 'POST':
            # Handle form submission for marking sales as fulfilled
            sale_infos = request.form.getlist('sale_info[]')
            for info in sale_infos:
                sale_id, product_key, sale_qty = info.split('-')
                sale_qty = int(sale_qty)
                avail_qty = Inventory.get_seller_product(seller_id, product_key).quantity
                if avail_qty >= sale_qty:
                    try:
                        Seller.order_fulfill(sale_id,product_key,seller_id)
                        # Deprecated-------------------------------
                        profit = app.db.execute('''
                            SELECT product_price * order_quantity * COALESCE(Discounts.discount_amount, 1)
                            FROM OrderHistory JOIN Products ON Products.seller_key = OrderHistory.seller_key AND Products.product_key = OrderHistory.product_key
                                 LEFT OUTER JOIN Discounts ON Discounts.discount_key = Products.product_discount_code
                            WHERE order_id= :order_id
                                  AND OrderHistory.product_key = :product_key
                                  AND OrderHistory.seller_key = :seller_id 
                            ''', product_key=product_key, seller_id=seller_id, order_id=sale_id)
                        User.edit_balance(seller_id, True, float(profit[0][0]))
                        # Deprecated-------------------------------
                        flash(f"Fulfilled order {sale_id}.")
                    except Exception as e:
                        print(e)
                else:
                    prod_name = app.db.execute('''
                                    SELECT product_name
                                    FROM Products
                                    WHERE product_key = :product_key
                                    ''', sale_id=sale_id, product_key=product_key, seller_id=seller_id)
                    flash(f"Not enough {prod_name} inventory for order: {sale_id}!!!")
        search_input = request.args.get('searchInput')
        search_criteria = request.args.get('searchCriteria')
        start_date = request.args.get('startDate') or None
        end_date = request.args.get('endDate') or None
        min_price = request.args.get('minPrice')
        max_price = request.args.get('maxPrice')
        selected_state = request.args.get('selected_state')
        sort, order = request.args.get('sort_by', "pname_asc", type=str).split('_')
        # Validate the search term and criteria
        valid = True
        if not search_input:
            valid = False
        elif search_criteria == 'OrderHistory.order_id':
            if not search_input.isdigit():
                flash("Invalid search!")
                valid = False
        else:
            if not search_input.replace(" ", "").isalpha():
                flash("Invalid search!")
                valid = False
        # Check if min_price is positive and convert it to float
        if min_price is not None and min_price.strip() != '' and float(min_price) >= 0:
            min_price = float(min_price)
        else:
            # Set a default positive value if min_price is not positive
            min_price = 0.0

        # Check if max_price is positive and convert it to float
        if max_price is not None and max_price.strip() != '' and float(max_price) >= 0:
            max_price = float(max_price)
        else:
            # Set a default positive value if max_price is not positive
            max_price = float('inf')
        page = request.args.get('page', 1, type=int)
        per_page = 15
        if valid:
            unfulfilled_sales = SaleHistory.get_unfulfilled(seller_id, sort, order, search_input.strip(), search_criteria, min_price, max_price, start_date, end_date, selected_state, page=page, per_page=per_page)
            unfulfilled_count = SaleHistory.count_unfulfilled(seller_id, search_input.strip(), search_criteria, min_price, max_price, start_date, end_date)
        else:
            unfulfilled_sales = SaleHistory.get_unfulfilled(seller_id, sort=sort, order=order, min_price=min_price, max_price=max_price, start_date=start_date, end_date=end_date, selected_state=selected_state, page=page, per_page=per_page)
            unfulfilled_count = SaleHistory.count_unfulfilled(seller_id, min_price=min_price, max_price=max_price, start_date=start_date, end_date=end_date, selected_state=selected_state)
        total_pages = math.ceil(unfulfilled_count / per_page)
        all_states = app.db.execute('''SELECT DISTINCT state FROM Zipcode ORDER BY state''')
        ratings = SaleHistory.get_buyer_ratings(seller_id)
        plt.figure(figsize=(10, 6))
        plt.barh(ratings['ratings'], ratings['counts'], color='darkcyan')
        plt.title('Rating Distribution')
        plt.xlabel('Counts')
        plt.ylabel('Ratings')
        plt.yticks(range(0, 6))
        plt.grid(axis='x')
        plt.tight_layout(pad=0.5)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plot = base64.b64encode(image_png).decode('utf-8')
        plt.close()
        return render_template('fulfill.html', unfulfilled_sales=unfulfilled_sales, 
                           current_page=page, total_pages=total_pages, seller_id=seller_id, all_states=all_states,plot=plot)
    else:
        redirect(url_for('index.index'))

@bp.route('/<int:seller_id>/PastSales', methods=['GET'])
@login_required
def past_orders(seller_id):
    if current_user.id == seller_id:
        is_seller = Seller.is_seller(seller_id)
        if not is_seller:
            redirect(url_for('users.profile'))
        search_input = request.args.get('searchInput')
        search_criteria = request.args.get('searchCriteria')
        start_date = request.args.get('startDate') or None
        end_date = request.args.get('endDate') or None
        min_price = request.args.get('minPrice')
        max_price = request.args.get('maxPrice')
        selected_state = request.args.get('selected_state')
        sort, order = request.args.get('sort_by', "pname_asc", type=str).split('_')
        # Validate the search term and criteria
        valid = True
        if not search_input:
            valid = False
        elif search_criteria == 'OrderHistory.order_id':
            if not search_input.isdigit():
                flash("Invalid search!")
                valid = False
        else:
            if not search_input.replace(" ", "").isalpha():
                flash("Invalid search!")
                valid = False
        # Check if min_price is positive and convert it to float
        if min_price is not None and min_price.strip() != '' and float(min_price) >= 0:
            min_price = float(min_price)
        else:
            # Set a default positive value if min_price is not positive
            min_price = 0.0

        # Check if max_price is positive and convert it to float
        if max_price is not None and max_price.strip() != '' and float(max_price) >= 0:
            max_price = float(max_price)
        else:
            # Set a default positive value if max_price is not positive
            max_price = float('inf')
        page = request.args.get('page', 1, type=int)
        per_page = 15
        if valid:
            past_sales = SaleHistory.get_fulfilled(seller_id, sort, order, search_input.strip(), search_criteria, min_price, max_price, start_date, end_date, selected_state, page=page, per_page=per_page)
            fulfilled_count = SaleHistory.count_fulfilled(seller_id, search_input.strip(), search_criteria, min_price, max_price, start_date, end_date)
        else:
            past_sales = SaleHistory.get_fulfilled(seller_id, sort, order, min_price=min_price, max_price=max_price, start_date=start_date, end_date=end_date, selected_state=selected_state, page=page, per_page=per_page)
            fulfilled_count = SaleHistory.count_fulfilled(seller_id, min_price=min_price, max_price=max_price, start_date=start_date, end_date=end_date, selected_state=selected_state)
        total_pages = math.ceil(fulfilled_count / per_page)
        all_states = app.db.execute('''SELECT DISTINCT state FROM Zipcode ORDER BY state''')
        ratings = SaleHistory.get_buyer_ratings(seller_id)
        plt.figure(figsize=(10, 6))
        plt.barh(ratings['ratings'], ratings['counts'], color='darkcyan')
        plt.title('Rating Distribution')
        plt.xlabel('Counts')
        plt.ylabel('Ratings')
        plt.yticks(range(0, 6))
        plt.grid(axis='x')
        plt.tight_layout(pad=0.5)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plot = base64.b64encode(image_png).decode('utf-8')
        plt.close()
        return render_template('sale_history.html', past_sales=past_sales, 
                           current_page=page, total_pages=total_pages, seller_id=seller_id, all_states=all_states, plot=plot)
    else:
        redirect(url_for('index.index'))

class ProductForm(FlaskForm):
    product_category = IntegerField('product_category', validators=[InputRequired(), NumberRange(min=0,max=22)])
    product_description = StringField('product_description', validators=[DataRequired()])
    product_quantity = IntegerField('product_quantity',validators=[NumberRange(min=0)])
    discount_amount = FloatField('discount_amount')
    update_submit = SubmitField('Update')
    delete_submit = SubmitField('Delete')

@bp.route('/<int:seller_id>/<int:product_id>/edit-product', methods=['GET', 'POST'])
@login_required
def edit_product(seller_id, product_id):
    form = ProductForm()
    product = Inventory.get_seller_product(seller_id, product_id)
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.delete_submit.data:
                message = Inventory.delete_product(seller_id, product_id)
                if product.discount_code:
                    Inventory.deleteCode(product.discount_code)
            else:
                if product.discount_code:
                    discount_code = product.discount_code
                    Inventory.updateCode(product.discount_code, form.discount_amount.data)
                else:
                    discount_code = Inventory.addCode(form.discount_amount.data)
                message = Inventory.update_product_info(seller_id, 
                                                        product_id,
                                                        form.product_category.data,
                                                        form.product_description.data,
                                                        form.product_quantity.data,
                                                        discount_code
                                                        )
            if message[:5] != "Error":
                flash(message)
                return redirect(url_for('users.profile'))
            else:
                flash(message)
        else:
            flash(f'Error! Product has not been Updated!\n {form.errors}')
    trends = SaleHistory.get_product_trend(seller_id, product_id)
    categories = app.db.execute('''SELECT cat_key, cat_name FROM Product_Category ORDER BY cat_name''')
    return render_template('edit_product.html', form=form, product=product, product_id=product_id, seller_id=seller_id, categories=categories, trends=trends)

@bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term')
    product_names = ["Lamball", "Cattiva", "Chikipi", "Lifmunk", "Foxparks", "Fuack", "Sparkit", "Tanzee", "Rooby", "Pengullet", 
        "Penking","Jolthog", "Jolthog Cryst", "Gumoss", "Vixy", "Hoocrates", "Teafant", "Depresso", "Cremis", "Daedream", "Rushoar", 
        "Nox", "Fuddler", "Killamari", "Mau", "Mau Cryst", "Celaray", "Direhowl", "Tocotoco", "Flopie", "Mozzarina", "Bristla", "Gobfin", "Gobfin Ignis",
        "Hangyu", "Hangyu Cryst", "Mossanda", "Woolipop", "Caprity", "Melpaca", "Eikthyrdeer", "Eikthyrdeer Terra", "Nitewing", "Ribbuny", "Incineram", "Cinnamoth", "Arsox",
        "Dumud", "Cawgnito", "Leezpunk", "Loupmoon", "Galeclaw", "Robinquill", "Robinquill Terra", "Gorirat", "Beegarde", "Elizabee", "Grintale", "Swee",
        "Sweepa", "Chillet", "Univolt", "Pyrin", "Pyrin Noct", "Reindrix", "Rayhound", "Kitsun", "Dazzi", "Lunaris", "Dinossom",
        "Surfent", "Maraith", "Digtoise", "Tombat", "Lovander", "Flambelle", "Vanwyrm", "Vanwyrm Cryst", "Bushi", "Beakon", "Ragnahawk", "Katress", 
        "Wixen", "Verdash", "Vaelet", "Sibelyx", "Elphidran", "Kelpsea", "Kelpsea Ignis", "Azurobe", "Cryolinx", "Blazehowl", "Relaxaurus", "Broncherry",
        "Petallia", "Reptyro", "Reptyro Cryst", "Kingpaca", "Kingpaca Cryst", "Mammorest", "Mammorest Cryst", "Wumpo", "Wumpo Botan", "Warsect", "Fenglope", "Felbat", "Quivern", "Blazamut", "Blazehowl Noct", "Helzephyr", "Astegon",
        "Menasting", "Anubis", "Jormuntide", "Jormuntide Ignis", "Suzaku", "Grizzbolt", "Lyleen", "Lyleen Noct", "Faleris", "Orserk", "Shadowbeak", "Paladius", "Necromus",
        "Frostallion", "Jetragon", "Bellanoir"
    ]
    suggestions = [name for name in product_names if term.lower() in name.lower()]
    return jsonify(suggestions)

class NewProductForm(FlaskForm):
    product_name = StringField('product_name', validators=[DataRequired()])
    product_category = IntegerField('product_category', validators=[InputRequired(), NumberRange(min=0,max=22)])
    product_description = StringField('product_description', validators=[DataRequired()])
    product_price = FloatField('product_price', validators=[DataRequired(), NumberRange(min=0.1)])
    product_quantity = IntegerField('product_quantity',validators=[DataRequired(), NumberRange(min=1)])
    discount_amount = StringField('discount_amount')
    submit = SubmitField('Post')

@bp.route('/<int:seller_id>/New_Product', methods=['GET', 'POST'])
@login_required
def post_product(seller_id):
    form = NewProductForm()
    if current_user.id == seller_id:
        is_seller = Seller.is_seller(seller_id)
        if not is_seller:
            redirect(url_for('users.profile'))
        if request.method == 'POST':
            if form.validate_on_submit():
                if request.form.get('discount_amount', None):
                    t = float(request.form.get('discount_amount', None))
                    newCode = Inventory.addCode(t)
                else:
                    newCode = None
                print (newCode, "NEW CODE IS HERE")
                message = Inventory.add_product(
                    seller_id,
                    request.form.get('product_name'),
                    request.form.get('product_category'),
                    request.form.get('product_description'),
                    request.form.get('product_price'),
                    request.form.get('product_quantity'),
                    newCode
                )
                flash(message)
                return redirect(url_for('users.profile'))
            else:
                flash(f'Error! Product has not been posted!\n {form.errors}')

        categories = app.db.execute('''SELECT cat_key, cat_name FROM Product_Category ORDER BY cat_name''')
        return render_template('new_product.html', form=form, seller_id=seller_id, categories=categories)
    else:
        redirect(url_for('index.index'))