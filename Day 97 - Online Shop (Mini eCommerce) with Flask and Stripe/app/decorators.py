from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'info')
            # 'next' guarda a página que ele tentava acessar
            return redirect(url_for('auth.login', next=request.path))

        if not current_user.is_admin:
            flash('Você precisa ser um administrador para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)

    return decorated_function
