
import pytest
from app import create_app, db
from app.models import User, Product, Order, OrderItem


@pytest.fixture(scope='function')
def test_app():
    app = create_app(config_name='testing')

    with app.app_context():
        db.create_all()

        admin = User(email="admin@test.com", is_confirmed=True, is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

        print("\n--- (Função) Banco de dados de TESTE (em memória) criado ---")

        yield app  


        db.drop_all()
        print("\n--- (Função) Banco de dados de TESTE (em memória) destruído ---")


@pytest.fixture(scope='function')
def client(test_app):
    with test_app.test_client() as test_client:
        with test_app.app_context():
            print("\n--- (Função) CLIENTE e APP_CONTEXT criados ---")
            yield test_client



@pytest.fixture(scope='function')
def regular_user(test_app):
    user = User(
        email="user@test.com",
        is_confirmed=True,
        is_admin=False
    )
    user.set_password("user123")
    db.session.add(user)
    db.session.commit()

    print("\n--- (Função) Usuário comum 'user@test.com' criado ---")

    yield user


    print("\n--- (Função) Usuário 'user@test.com' será limpo pelo drop_all ---")



@pytest.fixture(scope='function')
def sample_product(test_app):  
    product = Product(
        name="Produto de Teste",
        price=10.00,
        description="Um item de teste",
        image_file="default.jpg"
    )
    db.session.add(product)
    db.session.commit()

    print(f"\n--- (Função) Produto de teste (ID: {product.id}) criado ---")

    yield product

    # A limpeza agora é feita pelo db.drop_all() do test_app
    print(f"\n--- (Função) Produto de teste será limpo pelo drop_all ---")
