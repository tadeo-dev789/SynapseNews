from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import create_db_and_tables, get_session
from app.models import New, Subscriber, MarketSnapshot, MarketItem
from app.services.news_service import run_update_logic
from app.services.email_service import send_daily_newsletter
from app.jobs.news_job import update_news_job
from app.jobs.market_job import update_market_snapshot

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_news_job, 'interval', minutes=360)
    scheduler.add_job(update_market_snapshot, 'interval', hours=1)
    scheduler.add_job(send_daily_newsletter, 'cron', hour=8, minute=0)
    #PRUEBAS
    # scheduler.add_job(update_news_job)
    # scheduler.add_job(update_market_snapshot)
    # scheduler.add_job(send_daily_newsletter)
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

@app.post("/api/subscribe")
def subscribe_newsletter(email: str, session: Session = Depends(get_session)):
    existing = session.exec(select(Subscriber).where(Subscriber.email == email)).first()
    if existing:
        return {"mensaje": "¡Ya estas suscrito, gracias!"}
    
    new_sub = Subscriber(email=email)
    session.add(new_sub)
    session.commit()
    return {"mensaje": "Suscripcion exitosa. Recibiras noticias pronto."}


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

