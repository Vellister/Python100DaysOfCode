from app.models import User  # <-- ADICIONADO
from app import db  # <-- ADICIONADO

def test_registration_page_loads(client):
    response = client.get('/auth/register')
    html_text = response.data.decode('utf-8')
    assert response.status_code == 200
    assert "Cadastrar Nova Conta" in html_text


def test_successful_registration(client, mocker):
    mocker.patch('app.auth.routes.send_confirmation_email')

    response = client.post('/auth/register', data={
        'email': 'newuser@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Login" in html_text  

    assert "Sua conta foi criada! Por favor, verifique seu email para ativá-la." in html_text

    user = User.query.filter_by(email='newuser@test.com').first()
    assert user is not None
    assert user.is_confirmed is False


def test_registration_with_existing_email(client):
    response = client.post('/auth/register', data={
        'email': 'admin@test.com',  
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    html_text = response.data.decode('utf-8')
    assert response.status_code == 200

    assert "Este email já está em uso. Por favor, escolha outro." in html_text


def test_login_with_unconfirmed_account(client):
    user = User(
        email='newuser@test.com',
        is_confirmed=False  # A parte importante
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    # ---------------------------------------------


    response = client.post('/auth/login', data={
        'email': 'newuser@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    html_text = response.data.decode('utf-8')


    assert response.status_code == 200
    assert "Login" in html_text
    # Agora o usuário existe, e a mensagem flash correta deve aparecer
    assert "Sua conta ainda não foi ativada. Por favor, verifique seu email." in html_text


def test_successful_login(client):
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)

    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Mini eCommerce" in html_text
    assert "Login" not in html_text
    assert "Logout" in html_text


def test_login_wrong_password(client):
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'SENHA-ERRADA'
    }, follow_redirects=True)

    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Logout" not in html_text
    assert "Login sem sucesso. Verifique o email e a senha." in html_text


def test_logout(client):
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)


    response = client.get('/auth/logout', follow_redirects=True)
    html_text = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Mini eCommerce" in html_text
    assert "Logout" not in html_text
    assert "Login" in html_text
