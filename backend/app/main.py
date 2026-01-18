from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from pydantic import BaseModel
from sqlmodel import Session, select

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import create_db_and_tables, get_session
from app.models import New, Subscriber, MarketSnapshot, MarketItem
from app.services.news_service import run_update_logic
from app.services.email_service import send_daily_newsletter, send_welcome_email
from app.jobs.news_job import update_news_job
from app.jobs.market_job import update_market_snapshot


class SubscribeRequest(BaseModel):
    email: str

class UnsubscribeRequest(BaseModel):
    email: str
    
@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_news_job, 'interval', minutes=360)
    scheduler.add_job(update_market_snapshot, 'interval', hours=1)
    scheduler.add_job(send_daily_newsletter, 'cron', hour=8, minute=0)
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
    return {"proyecto": "SynapseNews", "status": "Online", "scheduler": "Active"}

@app.post("/api/update-markets/now")
def force_market_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_market_snapshot)
    return {"status": "Iniciado", "mensaje": "Actualizando datos de mercado en segundo plano..."}


@app.post("/api/subscribe")
def suscribe_newsletter(request: SubscribeRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    email = request.email
    existing = session.exec(select(Subscriber).where(Subscriber.email == email)).first()
    
    if existing:
        if existing.is_active:
            return {"mensaje": "¡Ya estás suscrito y activo!"}
        else:
            existing.is_active = True
            session.add(existing)
            session.commit()
            
            background_tasks.add_task(send_welcome_email, email)
            return {"mensaje": "¡Bienvenido de vuelta! Tu suscripción ha sido reactivada."}
    
    new_sub = Subscriber(email=email, is_active=True)
    session.add(new_sub)
    session.commit()
    
    # Enviar correo en segundo plano (No traba la API)
    background_tasks.add_task(send_welcome_email, email)
    
    return {"mensaje": "Suscripción exitosa. Revisa tu correo de bienvenida."}

@app.post("/api/unsubscribe")
def unsubscribe_newsletter(request: UnsubscribeRequest, session: Session = Depends(get_session)):
    email = request.email
    subscriber = session.exec(select(Subscriber).where(Subscriber.email == email)).first()
    
    if not subscriber:
        raise HTTPException(status_code=404, detail="Este correo no está registrado.")
    
    if not subscriber.is_active:
        return {"mensaje": "Este correo ya estaba desuscrito."}
    
    subscriber.is_active = False
    session.add(subscriber)
    session.commit()
    
    return {"mensaje": "Te has desuscrito correctamente. Lamentamos verte partir."}

@app.post("/api/trigger-newsletter")
def trigger_newsletter(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_daily_newsletter)
    return {"status": "Enviando", "mensaje": "Enviando correos en segundo plano..."}


@app.get("/api/news")
def get_news(page: int = 1, limit: int =10, category:Optional[str]=None,session: Session = Depends(get_session)):
    offset = (page -1) * limit
    query = select(New)

    if category:
        query = query.where(New.category == category)

    total = len(session.exec(query).all())
    news = session.exec(
    query.order_by(New.created_at.desc())
    .offset(offset)
    .limit(limit)
    ).all()
    
    return {
        "data": news,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@app.post("/api/update-news/{category}")
def update_news_feed(category: str, background_tasks: BackgroundTasks):
    if category not in ["tecnologia", "negocios"]:
        raise HTTPException(status_code=400, detail="Categoría invalida.")
    
    background_tasks.add_task(run_update_logic, category)
    return {"status": "Iniciado", "mensaje": f"Actualizando {category} en segundo plano ..."}

@app.get("/api/markets")
def get_markets(session: Session = Depends(get_session)):
    snapshot = session.exec(
        select(MarketSnapshot).order_by(MarketSnapshot.snapshot_date.desc())
    ).first()

    if not snapshot:
        return {"acciones": [], "cripto": []}

    items = session.exec(
        select(MarketItem).where(MarketItem.snapshot_id == snapshot.id)
    ).all()

    return {
        "acciones": [i for i in items if i.type == "stock"],
        "cripto": [i for i in items if i.type == "crypto"],
        "date": snapshot.snapshot_date
    }

