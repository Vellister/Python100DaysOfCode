from app.models import Product

def test_admin_dashboard_guest_redirects_to_login(client):
    response = client.get('/admin/', follow_redirects=True)
    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Login" in html_text
    assert "Por favor, faça login para acessar esta página." in html_text


def test_admin_dashboard_regular_user_redirects_to_index(client, regular_user):
    """(ESTE TESTE JÁ ESTÁ PASSANDO)"""
    client.post('/auth/login', data={
        'email': 'user@test.com',
        'password': 'user123'
    }, follow_redirects=True)
    response = client.get('/admin/', follow_redirects=True)
    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Nossos Produtos" in html_text
    assert "Painel Admin" not in html_text
    assert "Você precisa ser um administrador para acessar esta página." in html_text


def test_admin_dashboard_admin_user_loads_ok(client):
    """(ESTE TESTE JÁ ESTÁ PASSANDO)"""
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)
    response = client.get('/admin/')
    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Painel Admin" in html_text
    assert 'href="/admin/products"' in html_text


def test_admin_add_product_as_admin(client, test_app):
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)

    product_data = {
        'name': 'Produto de Teste Pytest',
        'price': 199.99,
        'description': 'Uma descricao de teste.',
        'image_file': 'teste.jpg'
    }


    response = client.post('/admin/product/new', data=product_data, follow_redirects=True)
    html_text = response.data.decode('utf-8')

    assert response.status_code == 200


    with test_app.app_context():
        product = Product.query.filter_by(name='Produto de Teste Pytest').first()
        assert product is not None
        assert product.price == 199.99


    assert "Produto de Teste Pytest" in html_text


    assert 'Produto &#34;Produto de Teste Pytest&#34; foi adicionado com sucesso!' in html_text
