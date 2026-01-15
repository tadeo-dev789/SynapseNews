from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.scraper import scrape_category

app = FastAPI()

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