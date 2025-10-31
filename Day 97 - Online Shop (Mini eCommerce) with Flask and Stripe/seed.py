from app import create_app, db
from app.models import Product


app = create_app()

with app.app_context():
    print("Iniciando o script para popular o banco de dados...")
    
    print("Limpando a tabela 'Product'...")
    Product.query.delete()

    print("Criando os 6 produtos padrão...")
    p1 = Product(name="Fone de Ouvido XYZ", price=299.90, description="Qualidade de som impecável.",
                 image_file="fone-de-ouvido.jpg")
    p2 = Product(name="Smartwatch Pro", price=850.00, description="Mantenha-se conectado e saudável.",
                 image_file="smartwatch.jpg")
    p3 = Product(name="Webcam Full HD", price=180.50, description="Perfeita para reuniões e streaming.",
                 image_file="webcam.jpg")
    p4 = Product(name="Mouse Gamer RGB", price=120.00, description="Precisão e iluminação personalizável.",
                 image_file="mouse-gamer.jpg")
    p5 = Product(name="Teclado Mecânico", price=350.00, description="Experiência de digitação superior.",
                 image_file="teclado-mecanico.jpg")
    p6 = Product(name="Câmera de Segurança", price=420.00, description="Monitore sua casa com segurança.",
                 image_file="camera-seguranca.jpg")

    db.session.add_all([p1, p2, p3, p4, p5, p6])

    db.session.commit()

    print("----------------------------------")
    print("Banco de dados populado com sucesso!")
    print("Verificação:")
    print(Product.query.all())
    print("----------------------------------")
