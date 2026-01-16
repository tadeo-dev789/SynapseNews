from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from datetime import datetime, date

from app.database import create_db_and_tables, get_session, SessionLocal
from app.models import New
from app.services.scraper import scrape_category
from app.services.ai_handler import rewrite_news

import time

def process_news_background(category: str, scraping_result:dict):
    
    session = SessionLocal()
    saved_count = 0
    
    try:
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
                session.commit()
                saved_count += 1
                
                time.sleep(10)
        print(f"Completado: {saved_count} noticias guardadas para {category}")
    except Exception as e:
        session.rollback()
        print(f" Error procesando {category}: {e}")
    finally:
        session.close()
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
        raise HTTPException(status_code=400, detail="Categoría inválida. Solo 'tecnologia' o 'negocios'.")
    
    # Ejecutar el scraper
    result = scrape_category(category)
    return result

@app.post("/api/update-news/{category}")
def update_news_feed(category: str, background_tasks: BackgroundTasks, session: Session = Depends(get_session), force: bool = False):
    
    if category not in ["tecnologia", "negocios"]:
        raise HTTPException(status_code=400, detail="Categoría inválida. Solo 'tecnologia' o 'negocios'.")
    
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
    
    if not scraping_result["data"] or len(scraping_result["data"]) == 0:
        return{
            "status": "No se encontraron noticias",
            "mensaje": "No se encontraron noticias nuevas en este momento",
            "nuevas_noticias": 0,
            "total_procesadas": 0
        } 
    background_tasks.add_task(process_news_background, category, scraping_result)
    return {
        "status": "Procesando de fondo",
        "mensaje": f"Se iniciará el procesamiento de {len(scraping_result['data'])} noticias",
        "total_encontradas": len(scraping_result["data"])
    }

@app.get("/api/news")
def get_news(session: Session = Depends(get_session)):
    # Devuelve las noticias ordenadas por fecha
    return session.exec(select(New).order_by(New.created_at.desc())).all()