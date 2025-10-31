import os
import requests
from flask import render_template, url_for


def send_confirmation_email(user):
    try:
        API_KEY = os.getenv('MAIL_PASSWORD')
        SENDER_EMAIL = os.getenv('MAIL_SENDER_EMAIL')

        print(f"[DEBUG 1] Credenciais carregadas")

        # Validação
        if not API_KEY or not SENDER_EMAIL:
            raise ValueError("MAIL_PASSWORD ou MAIL_SENDER_EMAIL não configurados")

        print(f"[DEBUG 2] Enviando email de {SENDER_EMAIL} para {user.email}")


        print(f"[DEBUG 3] Gerando token...")
        token = user.get_confirmation_token()
        print(f"[DEBUG 4] Token gerado: {token[:20]}...")

        print(f"[DEBUG 5] Gerando URL de confirmação...")
        confirm_url = url_for('auth.confirm_token', token=token, _external=True)
        print(f"[DEBUG 6] URL gerada: {confirm_url}")


        print(f"[DEBUG 7] Renderizando template...")
        html_body = render_template('email/confirm_user.html', confirm_url=confirm_url)
        print(f"[DEBUG 8] Template renderizado (primeiros 100 chars): {html_body[:100]}")


        url = "https://api.sendgrid.com/v3/mail/send"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "personalizations": [
                {
                    "to": [{"email": user.email}]
                }
            ],
            "from": {
                "email": SENDER_EMAIL,
                "name": "Equipe Mini eCommerce"
            },
            "subject": "Confirme sua Conta - Mini eCommerce",
            "content": [
                {
                    "type": "text/html",
                    "value": html_body
                }
            ]
        }

        print(f"[DEBUG 9] Enviando requisição para SendGrid...")


        response = requests.post(url, headers=headers, json=data)

        print(f"[DEBUG 10] Resposta recebida: {response.status_code}")

        if response.status_code == 202:
            print(f"✅ Email enviado com sucesso! Status: {response.status_code}")
        else:
            print(f"❌ Erro do SendGrid: {response.status_code}")
            print(f"Resposta: {response.text}")
            raise Exception(f"Falha ao enviar email: {response.text}")

    except Exception as e:
        print(f"❌ ERRO CAPTURADO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e
