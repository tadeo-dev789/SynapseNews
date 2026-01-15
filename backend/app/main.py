from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from datetime import datetime, date

from app.database import create_db_and_tables, get_session
from app.models import New
from app.services.scraper import scrape_category
from app.services.ai_handler import rewrite_news

import time


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    yield
    
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
    return {"proyecto": "SynapseNews", "status": "Online ", "mode": "Hackathon"}

@app.get("/api/scrape/{category}")
def trigger_scrape(category: str):
    if category not in ["tecnologia", "negocios"]:
        return {"error": "Categoría inválida. Solo 'tecnologia' o 'negocios'."}
    
    # Ejecutar el scraper
    result = scrape_category(category)
    return result

@app.post("/api/update-news/{category}")
def update_news_feed(category: str,force: bool = False, session: Session = Depends(get_session)):
    print(f"Lanzando scraper para: {category}")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_news = session.exec(select(New).where(New.category == category).where(New.created_at >= today_start)).all()
    
    if len(today_news) > 0 and not force:
        print(f"Ya existen {len(today_news)} noticias de hoy. No se hara scraping.")
        return {
            "status":"Al dia (Cache)",
            "mensaje": "Ya tienes las noticias de hoy, no hay necesidad de gastar recursos.",
            "total_disponibles": len(today_news)
        }
    
    print(f"No hay noticias frescas. Lanzando scraper para: {category}")
    
    scraping_result = scrape_category(category)
    
    if "error" in scraping_result:
        raise HTTPException(status_code=500, detail=scraping_result["error"])
    
    saved_count = 0
    
    for item in scraping_result["data"]:
        
        existing = session.exec(select(New).where(New.url == item["url"])).first()
    
        if not existing:
            texto_base = item.get("full_text",item["original_title"])
            print(f"Creando nota original para: {item['original_title'][:20]}...")
            
            contenido_original = rewrite_news(texto_base, category)
            
            new_entry = New(
                original_title = item["original_title"],
                url = item["url"],
                category = category,
                ai_summary = contenido_original
            )
            session.add(new_entry)
            saved_count += 1
            
            time.sleep(10)
    
    session.commit()
    
    return {
        "status": "Contenido generado exitosamente",
        "nuevas_notas": saved_count,
        "total_procesadas": len(scraping_result["data"])
    }

@app.get("/api/news")
def get_news(session: Session = Depends(get_session)):
    # Devuelve las noticias ordenadas por fecha
    return session.exec(select(New).order_by(New.created_at.desc())).all()