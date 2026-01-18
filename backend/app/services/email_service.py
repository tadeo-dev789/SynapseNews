import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select
from app.models import New, Subscriber
from app.database import engine
from datetime import datetime
from app.config import settings


def generate_newsletter_body(news_list):
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #f4f4f4; padding: 20px; text-align: center;">
            <h1 style="color: #2c3e50;">📢 SynapseNews</h1>
            <p>Tu dosis diaria de tecnología y negocios</p>
        </div>
        <div style="padding: 20px;">
    """
    
    for news in news_list:
        html += f"""
        <div style="margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
            <h2 style="color: #2980b9; margin-top: 0;">{news.original_title}</h2>
            <p style="font-size: 16px; line-height: 1.5;">{news.ai_summary}</p>
            <a href="{news.url}" style="background-color: #3498db; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 14px;">Leer nota completa</a>
        </div>
        """
        
    html += """
        </div>
        <div style="background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px;">
            <p>Estás recibiendo esto porque te suscribiste a SynapseNews.</p>
        </div>
    </body>
    </html>
    """
    return html
    
def send_email(subject, body, to_email):
    sender_email = settings.SMTP_USER
    password = settings.SMTP_PASSWORD
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    
    msg = MIMEMultipart()
    msg['From'] = f"SynapseNews Bot <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body,'html'))
    
    try:
        server = smtplib.SMTP(smtp_server,smtp_port)
        server.starttls()
        server.login(sender_email,password)
        text = msg.as_string()
        server.sendmail(sender_email,to_email,text)
        server.quit()
        return True
    except Exception as e:
        print(f"ERROR ENVIANDO EL EMAIL A {to_email}: {e}")
        return False

def send_welcome_email(to_email):
    subject = "¡Bienvenido a SynapseNews! 🚀"
    body = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #f4f4f4; padding: 20px; text-align: center;">
            <h1 style="color: #2c3e50;">Bienvenido a SynapseNews</h1>
            <p>Inteligencia Artificial aplicada a los mercados.</p>
        </div>
        <div style="padding: 20px; max-width: 600px; margin: 0 auto;">
            <p>Hola,</p>
            <p>Tu suscripción ha sido confirmada. A partir de mañana recibirás:</p>
            <ul>
                <li>Resúmenes concisos de Tecnología.</li>
                <li>Análisis de tendencias de Negocios.</li>
            </ul>
            <p style="font-size: 12px; color: #777; margin-top: 30px;">
                Si deseas desuscribirte, puedes hacerlo desde nuestra plataforma web.
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject,body, to_email)


def send_daily_newsletter():
    print("Iniciando proceso de envío de Newsletter...")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    with Session(engine) as session:

        todays_news = session.exec(
            select(New)
            .where(New.created_at >= today_start)
            .order_by(New.created_at.desc())
            .limit(10)
        ).all()
        
        if not todays_news:
            print("No hay noticias hoy para enviar.")
            return

        print(f"Seleccionadas {len(todays_news)} noticias más relevantes del día para el newsletter")

        subscribers = session.exec(select(Subscriber).where(Subscriber.is_active == True)).all()
        
        if not subscribers:
            print("No hay suscriptores activos.")
            return


        email_content = generate_newsletter_body(todays_news)
        date_str = datetime.now().strftime("%d/%m/%Y")
        subject = f"Las noticias de hoy ({date_str}) - SynapseNews"
        

        print(f"Enviando a {len(subscribers)} suscriptores...")
        count = 0
        for sub in subscribers:
            if send_email(subject, email_content, sub.email):
                print(f"   ✅ Enviado a: {sub.email}")
                count += 1
            
        print(f"Newsletter finalizado. Enviados: {count}/{len(subscribers)}")
