from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from pathlib import Path
import os
import time

env_path = Path (__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

SOURCES = {
    "tecnologia": "https://www.bbc.com/innovation",
    "negocios": "https://www.bbc.com/business"
}

def get_driver():
    selenium_url = os.getenv("SELENIUM_URL")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    
    options.add_argument("--blink-settings=imagesEnabled=false")#Este argumento bloquea las imagenes y CSS para que cargue en milisegundos
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    options.page_load_strategy = 'eager'
    return webdriver.Remote(
        command_executor=selenium_url,
        options=options
    )

def get_article_body(driver,url):
    try:
        print(f"Leyendo el cuerpo de: {url[:40]}...")
        driver.get(url)
        time.sleep(1.5)# dejamos un tiempo de espera de como 1.5 seg
        
        paragraphs = driver.find_elements(By.TAG_NAME,"p") # Encontramos todos los parrafos etiqueta <p>
        
        text_cont = []
        
        for p in paragraphs[:10]:
            text = p.text.strip()
            if len(text) > 20: #Aqui lo que hace es ignorar los textos que son cortos en la noticia
                text_cont.append(text)
        
        full_text = " ".join(text_cont)
        
        return full_text if full_text else "No se pudo extraer texto."
    
    except Exception as e:
        print(f"   ⚠️ Error leyendo artículo: {e}")
        return "Error extrayendo contenido."
    
    
def scrape_category(category_key: str):
    if category_key not in SOURCES:
        return {"error" : "Categoria no registrada"}
    
    url = SOURCES[category_key]
    driver = get_driver()
    news_list = []
    
    try:
        print(f"Se están buscando titulares en: {url}")
        driver.get(url)
        time.sleep(2)
        
        links_found = []
        elements = driver.find_elements(By.TAG_NAME,"h2")
        
        for el in elements:
            try:
                link_el = el.find_element(By.XPATH,"./ancestor::a")
                href = link_el.get_attribute("href")
                title = el.text.strip()
                
                if title and href and len(title) > 15:
                    links_found.append({"title": title, "url": href})
                
            except:
                continue
            
        unique_links = {v['url']:v for v in links_found}.values()
        
        black_list = [
            "newsletter", 
            "signup", 
            "cloud.email.bbc", 
            "/sport/",
            "/reel/",       
            "register",
            "login"
        ]
        for item in unique_links:
            
            if len(news_list) >= 10:
                break
            
            url_lower = item["url"].lower()
            
            if any(banned in url_lower for banned in black_list):
                print("SALTANDO PUBLICIDAD")
                continue
            
            body_text = get_article_body(driver, item["url"])
            
            # Si logramos sacar texto, lo guardamos
            if len(body_text) > 100:
                news_list.append({
                    "original_title": item["title"],
                    "url": item["url"],
                    "category": category_key,
                    "full_text": body_text
                })
        
        return {
            "category": category_key, 
            "count": len(news_list), 
            "data": news_list
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()

        
            