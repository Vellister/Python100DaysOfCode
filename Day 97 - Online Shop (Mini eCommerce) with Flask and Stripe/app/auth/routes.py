from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import auth_bp
from app import db, bcrypt
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.auth.utils import send_confirmation_email 


@auth_bp.route('/register', methods=['GET', 'POST'])
def register(): 
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, is_confirmed=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        try:
            send_confirmation_email(user)
            # Atualiza a mensagem flash
            flash('Sua conta foi criada! Por favor, verifique seu email para ativá-la.', 'success')
        except Exception as e:
            # (Opcional) Lógica de erro se o SendGrid falhar
            print(f"Erro ao enviar email: {e}")
            db.session.rollback()  # Desfaz a criação do usuário se o email falhar
            flash('Desculpe, houve um erro ao criar sua conta. Tente novamente.', 'danger')
            return render_template('register.html', title='Cadastrar', form=form)
        # --------------------------------------------------

        # Redireciona para a página de login para que ele espere o email
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Cadastrar', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):


            if not user.is_confirmed:
                flash('Sua conta ainda não foi ativada. Por favor, verifique seu email.', 'warning')
                # (Opcional: Adicionar lógica para reenviar email aqui)
                return redirect(url_for('auth.login'))
            # ------------------------------------------------------


            login_user(user, remember=form.remember.data)


            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login sem sucesso. Verifique o email e a senha.', 'danger')

    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))



@auth_bp.route('/confirm/<token>')
def confirm_token(token):
    """Rota para validar o token enviado por email."""


    if current_user.is_authenticated:
        return redirect(url_for('main.index'))


    user_id = User.verify_confirmation_token(token)

    if not user_id:
        # Token é inválido ou expirou (30 minutos)
        flash('O link de confirmação é inválido ou expirou.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)

    if user.is_confirmed:
        flash('Sua conta já está ativada. Por favor, faça login.', 'info')
    else:
        # Ativa a conta!
        user.is_confirmed = True
        db.session.commit()
        flash('Sua conta foi ativada com sucesso! Você já pode fazer login.', 'success')

    return redirect(url_for('auth.login'))
