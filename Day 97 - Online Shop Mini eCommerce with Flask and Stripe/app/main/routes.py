import stripe
import os
import time
from flask import (render_template, request, redirect, url_for, session,
                   flash, current_app, Response)
from flask_login import login_required, current_user
from app.main import main_bp
from app import db
from app.models import Product, Order, OrderItem



@main_bp.route('/', methods=['GET', 'POST'])
def index():
    print("--- DEBUG: Rota INDEX (versao 2) foi acessada ---", flush=True)
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        cart = session.get('cart', {})
        if not isinstance(cart, dict): cart = {}

        product = Product.query.get(product_id)
        if product:
            cart[product_id] = cart.get(product_id, 0) + 1
            session['cart'] = cart
            flash(f'{product.name} adicionado ao carrinho!', 'success')
        else:
            flash('Produto não encontrado.', 'danger')
        return redirect(url_for('main.index'))

    products = Product.query.all()
    return render_template('index.html', products=products)


@main_bp.route('/cart')
def cart():
    cart_dict = session.get('cart', {})
    cart_items = []
    grand_total = 0.0

    if isinstance(cart_dict, dict):
        for product_id, quantity in cart_dict.items():
            product_details = Product.query.get(product_id)

            if product_details:
                subtotal = product_details.price * quantity
                cart_items.append({
                    'id': product_id, 'name': product_details.name,
                    'price': product_details.price,
                    'image': product_details.image_file,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                grand_total += subtotal

    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)


@main_bp.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    cart = session.get('cart', {})
    if not isinstance(cart, dict): cart = {}
    try:
        quantity = int(request.form.get('quantity'))
        if quantity > 0:
            cart[product_id] = quantity
        else:
            cart.pop(product_id, None)
    except (ValueError, TypeError):
        pass
    session['cart'] = cart
    return redirect(url_for('main.cart'))


@main_bp.route('/remove_from_cart/<product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if isinstance(cart, dict) and product_id in cart:
        cart.pop(product_id)
        session['cart'] = cart
        flash('Produto removido do carrinho.', 'info')
    return redirect(url_for('main.cart'))


@main_bp.route('/checkout')
@login_required
def checkout():
    cart_dict = session.get('cart', {})
    if not cart_dict or not isinstance(cart_dict, dict):
        flash('Seu carrinho está vazio.', 'info')
        return redirect(url_for('main.cart'))

    line_items = []
    cart_items_details = []
    grand_total = 0.0

    for product_id, quantity in cart_dict.items():
        product_details = Product.query.get(product_id)

        if product_details:
            line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {'name': product_details.name},
                    'unit_amount': int(product_details.price * 100),
                },
                'quantity': quantity,
            })
            cart_items_details.append({
                'product': product_details,
                'quantity': quantity,
                'price_per_item': product_details.price
            })
            grand_total += product_details.price * quantity

    try:
        new_order = Order(
            total_price=grand_total,
            status="Pendente",
            customer=current_user
        )
        db.session.add(new_order)
        db.session.commit()

        for item in cart_items_details:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price_per_item=item['price_per_item']
            )
            db.session.add(order_item)

        db.session.commit()

        YOUR_DOMAIN = current_app.config['YOUR_DOMAIN']

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + url_for('main.success'),
            cancel_url=YOUR_DOMAIN + url_for('main.cancel'),
            metadata={'order_id': new_order.id}
        )

        new_order.stripe_session_id = checkout_session.id
        db.session.commit()

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao processar pedido: {e}', 'danger')
        return redirect(url_for('main.cart'))



@main_bp.route('/success')
@login_required
def success():
    try:
        order = Order.query.filter_by(customer=current_user, status="Pendente").order_by(
            Order.created_at.desc()).first()

        if order:
            order.status = "Concluído"
            db.session.commit()
            print(f"WORKAROUND: Pedido {order.id} atualizado para 'Concluído' via /success.")
        else:
            print("WORKAROUND: Rota /success chamada, mas nenhum pedido 'Pendente' foi encontrado.")
    except Exception as e:
        print(f"ERRO no workaround /success: {e}")
        db.session.rollback()

    session.pop('cart', None)
    flash('Pagamento realizado com sucesso! Seu pedido foi confirmado.', 'success')
    return render_template('success.html')


@main_bp.route('/cancel')
def cancel():
    flash('Pagamento cancelado.', 'warning')
    return render_template('cancel.html')


@main_bp.route('/order-history')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order_history.html', orders=orders)



@main_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=400)

    if event.type == 'checkout.session.completed':
        session_data = event.data.object
        order_id = session_data.metadata.get('order_id')
        try:
            order = Order.query.get(order_id)
            if order:
                order.status = "Concluído"
                db.session.commit()
        except Exception as e:
            return Response(status=500)

    return Response(status=200)


@main_bp.route('/teste123')
def rota_de_teste():
    return "<h1>Funciona! O deploy (v2) esta atualizado.</h1>"
