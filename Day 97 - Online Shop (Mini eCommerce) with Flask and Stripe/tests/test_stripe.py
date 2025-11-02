import stripe
from app.models import Order, OrderItem
from app import db
import time


def test_checkout_redirects_to_stripe(client, regular_user, sample_product, mocker):
    fake_session = mocker.Mock(
        url='https://fake.stripe.url/checkout-session',
        id='sess_fake_12345'
    )
    mocker.patch('stripe.checkout.Session.create', return_value=fake_session)

    client.post('/auth/login', data={'email': 'user@test.com', 'password': 'user123'})

    with client.session_transaction() as sess:
        sess['cart'] = {str(sample_product.id): 1}

    response = client.get('/checkout') 


    order = Order.query.filter_by(user_id=regular_user.id).first()
    assert order is not None
    assert order.status == "Pendente"
    assert order.total_price == sample_product.price
    assert order.stripe_session_id == 'sess_fake_12345'


    assert response.status_code == 303
    assert response.location == 'https://fake.stripe.url/checkout-session'



def test_success_route_completes_order(client, regular_user, test_app):
    client.post('/auth/login', data={'email': 'user@test.com', 'password': 'user123'})


    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}


    order = Order(
        total_price=50.00,
        status="Pendente",
        customer=regular_user,  
        stripe_session_id='sess_teste_manual'
    )
    db.session.add(order)
    db.session.commit()
    order_id = order.id  


    response = client.get('/success', follow_redirects=True)
    html_text = response.data.decode('utf-8')


    assert response.status_code == 200
    assert "Pagamento realizado com sucesso! Seu pedido foi confirmado." in html_text


    with test_app.app_context():
        completed_order = Order.query.get(order_id)
        assert completed_order.status == "Concluído"


    with client.session_transaction() as sess:
        assert 'cart' not in sess or sess['cart'] == {}
