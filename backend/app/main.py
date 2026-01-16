from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from datetime import datetime, date

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import create_db_and_tables, get_session, SessionLocal
from app.models import New, Subscriber
from app.services.scraper import scrape_category
from app.services.ai_handler import rewrite_news
from app.services.email_service import send_daily_newsletter

import time

def run_update_logic(category: str):
    session = SessionLocal()
    try:
        existing_urls = session.exec(select(New.url).where(New.category == category)).all()
        
        scraping_result = scrape_category(category, ignore_urls=existing_urls)
        
        if "error" in scraping_result:
            print(f"Error en auto-update {category}: {scraping_result['error']}")
            return
    
        saved_count = 0
        
        for item in scraping_result.get("data", []):
        
            existing = session.exec(select(New).where(New.url == item["url"])).first()
        
            if not existing:
                texto_base = item.get("full_text",item["original_title"])
                print(f"Creando nota original para: {item['original_title'][:20]}...")
                
                contenido_completo = rewrite_news(texto_base, category)
                
                partes = contenido_completo.replace('\r\n', '\n').split('\n\n', 1)
                
                if len(partes) >= 2:
                    titulo_espanol = partes[0].strip().replace("**", "")
                    cuerpo_espanol = partes[1].strip()
                else:
                    titulo_espanol = item["original_title"]
                    cuerpo_espanol = contenido_completo
                    
                new_entry = New(
                    original_title = titulo_espanol,
                    url = item["url"],
                    category = category,
                    ai_summary = cuerpo_espanol
                )
                session.add(new_entry)
                session.commit()
                saved_count += 1 
                time.sleep(10)
                
        print(f"Completado: {saved_count} noticias guardadas para {category}")
    except Exception as e:
        session.rollback()
        print(f" Error procesando {category}: {e}")
    finally:
        session.close()

def scheduled_tasks():
    print("EJECUTANDO TAREAS PROGRAMADAS...") 
    run_update_logic("tecnologia")
    run_update_logic("negocios")
    

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_tasks, 'interval', minutes=360)
    scheduler.add_job(scheduled_tasks)
    scheduler.add_job(send_daily_newsletter, 'cron', hour=8, minute=0)
#    scheduler.add_job(send_daily_newsletter)
    scheduler.start()
    print("SCHEDULER INICIADO: Actualización automática activa.")
    
    yield
    
    scheduler.shutdown()
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"proyecto": "SynapseNews", "status": "Online 🟢", "scheduler": "Active"}

@app.post("/api/subscribe")
def subscribe_newsletter(email: str, session: Session = Depends(get_session)):
    existing = session.exec(select(Subscriber).where(Subscriber.email == email)).first()
    if existing:
        return {"mensaje": "¡Ya estás suscrito, gracias!"}
    
    new_sub = Subscriber(email=email)
    session.add(new_sub)
    session.commit()
    return {"mensaje": "✅ Suscripción exitosa. Recibirás noticias pronto."}


@app.post("/api/trigger-newsletter")
def trigger_newsletter(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_daily_newsletter)
    return {"status": "Enviando", "mensaje": "Enviando correos en segundo plano..."}


@app.get("/api/news")
def get_news(session: Session = Depends(get_session)):
    return session.exec(select(New).order_by(New.created_at.desc())).all()


@app.post("/api/update-news/{category}")
def update_news_feed(category: str, background_tasks: BackgroundTasks):
    if category not in ["tecnologia", "negocios"]:
        raise HTTPException(status_code=400, detail="Categoría inválida.")
    
    background_tasks.add_task(run_update_logic, category)
    return {"status": "Iniciado", "mensaje": f"Actualizando {category} en segundo plano ..."}