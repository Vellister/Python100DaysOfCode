def test_index_page_loads(client):
    response = client.get('/')


    html_text = response.data.decode('utf-8')

    assert response.status_code == 200


    assert "Mini eCommerce" in html_text
    assert "Login" in html_text


def test_cart_page_loads(client):
    response = client.get('/cart')

    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Seu Carrinho" in html_text  

    assert "Seu carrinho está vazio." in html_text
