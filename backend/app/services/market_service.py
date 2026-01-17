import requests
from datetime import date, timedelta
from app.config import settings

EOD_URL = "https://eodhistoricaldata.com/api/eod"


def _get_last_trading_data(symbol_api: str, days_back: int = 5, include_previous: bool = False) -> tuple:

    today = date.today()
    
    # Intentar con los últimos N días hasta encontrar datos
    for days in range(days_back):
        check_date = (today - timedelta(days=days)).isoformat()
        
        try:
            r = requests.get(
                f"{EOD_URL}/{symbol_api}",
                params={
                    "api_token": settings.EODHD_API_KEY,
                    "from": check_date,
                    "to": check_date,
                    "fmt": "json"
                },
                timeout=10
            )
            
            if r.status_code == 200:
                data = r.json()
                if data and len(data) > 0:
                    data_today = data[0]
                    data_previous = None
                    
                    # Si necesitamos el día anterior para calcular cambio
                    if include_previous and days < days_back - 1:
                        prev_date = (today - timedelta(days=days + 1)).isoformat()
                        try:
                            r_prev = requests.get(
                                f"{EOD_URL}/{symbol_api}",
                                params={
                                    "api_token": settings.EODHD_API_KEY,
                                    "from": prev_date,
                                    "to": prev_date,
                                    "fmt": "json"
                                },
                                timeout=10
                            )
                            if r_prev.status_code == 200:
                                prev_data = r_prev.json()
                                if prev_data and len(prev_data) > 0:
                                    data_previous = prev_data[0]
                        except:
                            pass
                    
                    return data_today, check_date, data_previous
        except:
            continue
    
    return None, None, None


def fetch_top_stocks():

    if not settings.TOP_STOCK_SYMBOLS:
        print("Advertencia: No hay símbolos de acciones configurados en TOP_STOCK_SYMBOLS")
        return []
    
    if not settings.EODHD_API_KEY:
        print("Error: EODHD_API_KEY no está configurada en el .env")
        return []
    
    stocks = []
    successful = 0
    failed = 0

    print(f"Iniciando obtención de datos de {len(settings.TOP_STOCK_SYMBOLS)} acciones...")

    for symbol in settings.TOP_STOCK_SYMBOLS:
        symbol_api = f"{symbol}.US"

        try:
            data, data_date, data_prev = _get_last_trading_data(symbol_api, days_back=5, include_previous=True)
            
            if not data:
                print(f"{symbol}: No se encontraron datos disponibles")
                failed += 1
                continue
            
            if "close" not in data:
                print(f"{symbol}: No se encontró el precio en la respuesta")
                failed += 1
                continue

            # Calcular cambio porcentual
            change_24h = None
            
            if "change_pct" in data and data.get("change_pct") is not None:
                change_24h = data.get("change_pct")
            elif data.get("change") is not None and data.get("close") is not None:
                current_price = data.get("close")
                change_abs = data.get("change")
                if current_price and change_abs:
                    prev_price = current_price - change_abs
                    if prev_price and prev_price != 0:
                        change_24h = (change_abs / prev_price) * 100
            elif data_prev and data_prev.get("close") is not None:
                current_price = data.get("close")
                prev_price = data_prev.get("close")
                if current_price and prev_price and prev_price != 0:
                    change_24h = ((current_price - prev_price) / prev_price) * 100
            
            stocks.append({
                "type": "stock",
                "symbol": symbol,
                "price": data.get("close"),
                "change_24h": change_24h,
                "market_cap": None,
                "image": None
            })
            successful += 1
            print(f"{symbol}: ${data.get('close')}")

        except requests.exceptions.Timeout:
            print(f"{symbol}: Error de conexión (timeout)")
            failed += 1
        except requests.exceptions.RequestException as e:
            print(f"{symbol}: Error de conexión")
            failed += 1
        except (KeyError, IndexError, ValueError) as e:
            print(f"{symbol}: Error procesando datos")
            failed += 1
        except Exception as e:
            print(f"{symbol}: Error inesperado")
            failed += 1

    print(f"Stocks: {successful} completados de {len(settings.TOP_STOCK_SYMBOLS)}")
    return stocks


def fetch_top_cryptos():

    print("Iniciando obtención de datos de criptomonedas...")
    
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1
            },
            timeout=10
        )

        if r.status_code != 200:
            print(f"CoinGecko API error: código {r.status_code}")
            return []

        data = r.json()
        if not data:
            print("No se recibieron datos de CoinGecko")
            return []

        cryptos = []
        for c in data:
            try:
                if "symbol" not in c or "current_price" not in c:
                    continue
                
                cryptos.append({
                    "type": "crypto",
                    "symbol": c["symbol"].upper(),
                    "price": c.get("current_price"),
                    "change_24h": c.get("price_change_percentage_24h"),
                    "market_cap": c.get("market_cap"),
                    "image": c.get("image")
                })
            except (KeyError, ValueError):
                continue

        print(f"Criptomonedas: {len(cryptos)} completadas")
        return cryptos

    except requests.exceptions.Timeout:
        print("CoinGecko API: Error de conexión (timeout)")
        return []
    except requests.exceptions.RequestException as e:
        print("CoinGecko API: Error de conexión")
        return []
    except Exception as e:
        print("CoinGecko API: Error procesando datos")
        return []


def fetch_market_data():

    stocks = fetch_top_stocks()
    cryptos = fetch_top_cryptos()
    total = stocks + cryptos
    
    print(f"Total: {len(stocks)} acciones + {len(cryptos)} criptos = {len(total)} items")
    
    return total
