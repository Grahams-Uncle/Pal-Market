from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask import current_app as app
from .models.cart import Cart
from .models.inventory import Inventory
from .models.user import User
from .models.order_history import OrderHistory
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_login import login_required, current_user

bp = Blueprint('cart', __name__)


@bp.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.get_cart_items_by_user_id(current_user.id)
    return render_template('cart.html', cart_items=cart_items)
    

@bp.route('/change_quantity', methods=['POST'])
@login_required
def change_quantity():
    cart_item_id = int(request.form.get('cart_item_id'))
    quantity = int(request.form.get('quantity'))
    total_price = float(request.form.get('total_price'))
    per_price = total_price/quantity
    print(f"Want to change quantity: {quantity}")
    if Cart.update_cart(cart_item_id, current_user.id, quantity, per_price):
        flash('Cart updated successfully!', 'success')
    else:
        print("Not working")
        pass

    return redirect(url_for('cart.view_cart'))


@bp.route('/remove_item/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_item(cart_item_id):
    print("want to remove")
    cart_item = Cart.get_cart_item(cart_item_id, current_user.id)
    if cart_item:
        Cart.remove_from_cart(cart_item_id, current_user.id)
        flash('Item removed from cart.', 'success')
    else:
        flash('Item not found in cart or you do not have permission to remove it.', 'error')

    return redirect(url_for('cart.view_cart'))


@bp.route('/submit_cart', methods=['POST'])
@login_required
def submit_entire_cart():
    print("want to submit 1")
    user_id = current_user.id
    try:
        cart_items = Cart.get_cart_items_by_user_id(user_id)
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('cart.view_cart'))

        total_price = 0
        for item in cart_items:
            seller_key = item['seller_key']  
            product_key = item['product_key']  
            quantity = item['quantity']

            
            inventory_item_quantity = Inventory.get_product_inventory(seller_key, product_key)
            if quantity > inventory_item_quantity:
                flash(f'Insufficient stock for {item["product_name"]}.', 'error')
                return redirect(url_for('cart.view_cart'))
            
            total_price += item['total_price']

        user_balance = User.get(user_id).balance
        if user_balance < total_price:
            flash(f'Insufficient balance to complete the purchase.', 'error')
            return redirect(url_for('cart.view_cart'))

        for item in cart_items:
            seller_key = item['seller_key']
            product_key = item['product_key']
            quantity = item['quantity']
            order_id = OrderHistory.add_order_history(user_id, product_key, seller_key, quantity)
            if order_id:
                flash(f'Order {order_id} placed successfully!', 'success')

        User.edit_balance(user_id, False, total_price)
        Cart.empty_cart(user_id)
        flash('Purchase successful!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('cart.view_cart'))


@bp.route('/submit_part_cart', methods=['POST'])
@login_required
def submit_part_of_cart():
    print("want to submit 2")
    user_id = current_user.id
    cart_item_ids = request.form.getlist('cart_item_ids')  

    if not cart_item_ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    try:
        for cart_id in cart_item_ids:
            cart_item = Cart.get_cart_item(cart_id, current_user.id)
            if not cart_item:
                flash('No such item.', 'warning')
                continue
                        
            inventory_item = Inventory.get_product_inventory(cart_item.seller_key, cart_item.product_key)
            if cart_item.quantity > inventory_item.quantity:
                flash(f'Insufficient stock for {cart_item.product_key}.', 'error')
                continue
            

            user_balance = User.get(user_id).user_balance
            if user_balance < cart_item.price:
                flash('Insufficient balance for {cart_item.product_key}.', 'error')
                continue
            
            
            OrderHistory.add_order_history(user_id, cart_item.product_key, cart_item.seller_key, cart_item.quantity)
            User.edit_balance(user_id, False, float(cart_item.price))
            Cart.remove_from_cart(cart_id)
            flash(f'{cart_item.product_key} purchase successful!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('cart.view_cart'))


    

