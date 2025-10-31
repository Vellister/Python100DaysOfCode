from flask import render_template, request, flash, redirect, url_for
from app.admin import admin_bp
from app.decorators import admin_required
from app import db
from app.models import Product, Order
from app.admin.forms import ProductForm


@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('dashboard.html', title="Painel Admin")


@admin_bp.route('/products')
@admin_required
def list_products():
    products = Product.query.all()
    return render_template('products.html', products=products, title="Gerenciar Produtos")


@admin_bp.route('/product/new', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image_file=form.image_file.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f'Produto "{new_product.name}" foi adicionado com sucesso!', 'success')
        return redirect(url_for('admin.list_products'))

    return render_template('product_form.html', form=form, title="Adicionar Produto", legend="Novo Produto")


@admin_bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        product.image_file = form.image_file.data

        db.session.commit()

        flash(f'Produto "{product.name}" foi atualizado com sucesso!', 'success')
        return redirect(url_for('admin.list_products'))

    return render_template('product_form.html', form=form, title="Editar Produto", legend=f"Editar {product.name}")


@admin_bp.route('/product/<int:product_id>/delete', methods=['GET'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Produto "{product_name}" foi deletado com sucesso!', 'success')
    return redirect(url_for('admin.list_products'))


@admin_bp.route('/orders')
@admin_required
def list_orders():
    """Mosta uma lista de todos os pedidos de todos os clientes."""
    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template('orders.html', orders=orders, title="Ver Pedidos")
