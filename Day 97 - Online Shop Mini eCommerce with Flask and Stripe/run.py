from app import create_app, db
from app.models import User, Product, Order, OrderItem
import os

config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Product=Product,
                Order=Order, OrderItem=OrderItem)

if __name__ == '__main__':
    app.run(debug=True)
