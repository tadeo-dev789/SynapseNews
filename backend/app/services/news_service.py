import time
from sqlmodel import select
from app.database import SessionLocal
from app.models import New
from app.services.scraper import scrape_category
from app.services.ai_handler import rewrite_news


def run_update_logic(category: str):
    print(f"INICIANDO LECTURA DE NOTICIAS EN {category}")
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
