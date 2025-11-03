from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length


class ProductForm(FlaskForm):
    name = StringField('Nome do Produto',
                       validators=[DataRequired(), Length(min=3, max=100)])

    price = FloatField('Preço (ex: 299.90)',
                       validators=[DataRequired(message="Por favor, insira um preço.")])

    description = TextAreaField('Descrição',
                                validators=[DataRequired()])

    image_file = StringField('Nome do Arquivo da Imagem (ex: produto.jpg)',
                             validators=[DataRequired()])

    submit = SubmitField('Salvar Produto')
