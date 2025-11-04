English | Português (BR)

🚀 Full-Stack Mini-E-Commerce (Flask & Stripe)
Status: 100% Complete and Deployed!

This project is a fully functional full-stack e-commerce application, built as part of a 100 Days of Code challenge. It demonstrates a complete shopping flow, from user registration (with email confirmation) and cart management to secure payment processing with Stripe and an admin panel for product and order management.

🔴 Live Deploy
Visit the live, functional version of this project hosted on Render:

https://python100daysofcode-mini-ecommerce-flask.onrender.com/

(Note: Render's free tier spins down services after 15 minutes of inactivity. The first load may take up to 50 seconds to "wake up" the server.)

✨ Core Features
This project goes beyond a simple "CRUD" app to implement complex, real-world functionalities:

1. Authentication & User Management
Account Registration: Users can create a new account.

Email Confirmation: On registration, an API call to SendGrid dispatches an email with a unique, secure confirmation token.

Login & Logout: Full session management using Flask-Login.

Order History: Logged-in users can view a "My Orders" page with their complete order history and status.

2. E-Commerce Flow
Dynamic Product Catalog: The home page dynamically loads all products from the database.

Session-Based Shopping Cart: A fully functional cart that allows users to:

Add items.

Update item quantities.

Remove items.

Dynamic Nav-Bar: The site's navigation bar shows the total item count in the cart in real-time.

3. Stripe Payment Integration
Secure Checkout: Integrates with the Stripe Checkout API. The Flask backend sends the cart items to Stripe to create a secure, hosted payment session (in test mode).

Order Creation: Before redirecting to Stripe, an order with "Pending" status is created in the database.

Real-Time Payment Confirmation (Stripe Webhook): The application exposes a secure /stripe-webhook endpoint to listen for real-time events from Stripe. When a payment is successful, Stripe sends a checkout.session.completed event, which the app securely verifies and uses to:

Find the corresponding "Pending" order in the database.

Update the order's status to "Completed".

(The /success route simply thanks the user and clears their cart).

4. Admin Dashboard
Restricted Access: The /admin panel is fully secured using a custom @admin_required decorator, which rejects non-admin users and unauthenticated guests.

Product CRUD: Logged-in admins can Create, Read, Update, and Delete products from the database.

Order Viewing: The admin can view a list of all orders from all customers in the system.

5. Automated Testing
High Coverage: The project includes a suite of 15 integration tests using Pytest and Pytest-Mock.

Logic Validation: The test suite automatically validates the registration flow, login logic (wrong password, unconfirmed account), admin permissions (blocking regular users), and the entire payment flow by "mocking" the Stripe and SendGrid APIs.

🛠️ Tech Stack
Backend: Flask, Gunicorn

Database: PostgreSQL (Production on Render) & SQLite (Development/Testing)

ORM: Flask-SQLAlchemy

Authentication: Flask-Login, Flask-Bcrypt

Forms: Flask-WTF (with validation)

Third-Party APIs: Stripe (Payments), SendGrid (Emails)

Testing: Pytest, Pytest-Mock

Frontend: HTML5, CSS3, Bootstrap 5

Deploy: Render

⚙️ How to Run Locally
Clone the repository:

Bash

git clone https://github.com/Vellister/Python100DaysOfCode.git
Navigate to the project folder:

Bash

cd "Python100DaysOfCode/Day 97 - Online Shop Mini eCommerce with Flask and Stripe"
Create and activate a virtual environment (venv):

Bash

python -m venv venv
.\venv\Scripts\Activate
Install all dependencies:

Bash

pip install -r requirements.txt
Create your .env file: Create a file named .env in the project root and add your secret keys:

Ini, TOML

# Flask secret key (can be any long, random string)
FLASK_SECRET_KEY=your_secret_key_here

# Stripe keys (from your Stripe dashboard, in test mode)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid keys (for email confirmation)
MAIL_PASSWORD=SG.your_sendgrid_api_key
MAIL_SENDER_EMAIL=your-verified-email@on-sendgrid.com
Create the local database (SQLite): Open the Flask shell and create the tables.

Bash

flask shell
>>> db.create_all()
>>> exit()
(Optional) Seed the database with products: Run the seed.py script to add the example products.

Bash

python seed.py
Run the app:

Bash

flask run
The site will be available at http://127.0.0.1:5000

🧪 Running the Tests
With your virtual environment (venv) activated and packages installed, you can run the full test suite at any time:

Bash

pytest
<hr>

🚀 Mini E-Commerce Full-Stack com Flask e Stripe
Status: 100% Concluído e no ar!

Este projeto é um aplicativo de e-commerce full-stack totalmente funcional, construído como parte de um desafio de 100 Dias de Código. Ele demonstra um fluxo de compra completo, desde o registro de usuário (com confirmação por e-mail) e gerenciamento de carrinho, até o pagamento seguro com Stripe e um painel de administração para gerenciamento de produtos e pedidos.

🔴 Deploy Ao Vivo
Visite a versão funcional do projeto hospedada no Render:

https://python100daysofcode-mini-ecommerce-flask.onrender.com/

(Nota: O plano gratuito do Render "coloca o site para dormir" após 15 minutos de inatividade. O primeiro carregamento pode demorar cerca de 50 segundos para "acordar" o servidor.)

✨ Funcionalidades Principais
Este projeto vai além de um simples "CRUD" e implementa funcionalidades complexas do mundo real:

1. Autenticação e Usuários
Registro de Conta: Usuários podem criar uma nova conta.

Confirmação por E-mail: Após o registro, uma chamada de API para o SendGrid envia um e-mail com um token de confirmação único e seguro.

Login & Logout: Sistema de sessão completo usando Flask-Login.

Histórico de Pedidos: Usuários logados podem ver uma página com todos os seus pedidos passados e seus status.

2. Fluxo de E-Commerce
Visualização de Produtos: Página inicial que carrega produtos dinamicamente do banco de dados.

Carrinho de Compras: Carrinho de compras 100% funcional baseado em sessão, permitindo:

Adicionar itens ao carrinho.

Atualizar a quantidade de itens.

Remover itens do carrinho.

Contagem Dinâmica: O menu de navegação exibe o número total de itens no carrinho em tempo real.

3. Pagamento e Pedidos (Integração com Stripe)
Checkout Seguro: Integração com a API do Stripe Checkout, onde o Flask envia os itens do carrinho para o Stripe criar uma sessão de pagamento segura (em modo de teste).

Criação de Pedidos: Antes de redirecionar para o Stripe, um pedido com status "Pendente" é criado no banco de dados.

Confirmação de Pagamento em Tempo Real (Stripe Webhook): A aplicação expõe um endpoint seguro /stripe-webhook para "ouvir" eventos em tempo real do Stripe. Quando um pagamento é bem-sucedido, o Stripe envia um evento checkout.session.completed, que o app verifica de forma segura e usa para:

Encontrar o pedido "Pendente" correspondente no banco de dados.

Atualizar o status do pedido para "Concluído".

(A rota /success apenas agradece o usuário e limpa o carrinho).

4. Painel de Administrador
Acesso Restrito: O painel /admin é totalmente protegido usando um decorador @admin_required, que barra visitantes e usuários comuns.

CRUD de Produtos: Administradores logados podem Criar, Ler, Atualizar e Deletar produtos do banco de dados.

Visualização de Pedidos: O admin pode ver uma lista de todos os pedidos de todos os clientes no sistema.

5. Testes Automatizados
Alta Cobertura: O projeto inclui uma suíte de 15 testes de integração usando Pytest e Pytest-Mock.

Testes de Lógica: A suíte valida automaticamente o fluxo de registro, a lógica de login (senha errada, usuário não confirmado), as permissões de admin (barrando usuários comuns) e o fluxo completo de pagamento, usando "mocks" para simular as APIs do Stripe e SendGrid.

🛠️ Tecnologias Utilizadas
Backend: Flask, Gunicorn

Banco de Dados: PostgreSQL (Produção no Render) & SQLite (Desenvolvimento/Testes)

ORM: Flask-SQLAlchemy

Autenticação: Flask-Login, Flask-Bcrypt

Formulários: Flask-WTF (com validação)

APIs de Terceiros: Stripe (Pagamentos), SendGrid (E-mails)

Testes: Pytest, Pytest-Mock

Frontend: HTML5, CSS3, Bootstrap 5

Deploy: Render

⚙️ Como Rodar o Projeto Localmente
Clone o repositório:

Bash

git clone https://github.com/Vellister/Python100DaysOfCode.git
Navegue até a pasta do projeto:

Bash

cd "Python100DaysOfCode/Day 97 - Online Shop Mini eCommerce with Flask and Stripe"
Crie e ative um ambiente virtual (venv):

Bash

python -m venv venv
.\venv\Scripts\Activate
Instale todas as dependências:

Bash

pip install -r requirements.txt
Crie seu arquivo .env: Crie um arquivo chamado .env na pasta raiz do projeto e adicione suas chaves secretas:

Ini, TOML

# Chave do Flask (pode ser qualquer string longa e aleatória)
FLASK_SECRET_KEY=sua_chave_secreta_aqui

# Chaves do Stripe (em modo de teste)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Chaves do SendGrid (para envio de email)
MAIL_PASSWORD=SG.sua_api_key_do_sendgrid
MAIL_SENDER_EMAIL=seu-email-verificado@no-sendgrid.com
Crie o Banco de Dados local (SQLite): Abra o shell do Flask e crie as tabelas.

Bash

flask shell
>>> db.create_all()
>>> exit()
(Opcional) Popule o banco com produtos: Rode o script seed.py para adicionar os produtos de exemplo.

Bash

python seed.py
Rode o aplicativo:

Bash

flask run
O site estará disponível em http://127.0.0.1:5000

🧪 Rodando os Testes
Com seu ambiente virtual (venv) ativado e os pacotes instalados, você pode rodar a suíte completa de 15 testes a qualquer momento:

Bash

pytest
