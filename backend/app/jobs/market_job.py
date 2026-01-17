from datetime import date
from sqlmodel import select
from app.database import SessionLocal
from app.models import MarketSnapshot, MarketItem
from app.services.market_service import fetch_market_data


def update_market_snapshot():
    session = SessionLocal()
    today = date.today()
    
    print(f"Iniciando actualización de snapshot de mercado para {today.isoformat()}")

    try:
        exists = session.exec(
            select(MarketSnapshot).where(MarketSnapshot.snapshot_date == today)
        ).first()

        if exists:
            print(f"Snapshot ya existe para {today.isoformat()}. Saltando actualización.")
            return

        print("Obteniendo datos de mercado desde APIs...")
        market_data = fetch_market_data()

        if not market_data or len(market_data) == 0:
            print("Error: No se obtuvieron datos de mercado. Verifica las configuraciones de API.")
            return

        print(f"Se obtuvieron {len(market_data)} items de mercado")

        snapshot = MarketSnapshot(snapshot_date=today)
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)
        
        print(f"Snapshot creado con ID: {snapshot.id}")

        items_added = 0
        for item_data in market_data:
            try:
                if not item_data.get("type") or not item_data.get("symbol"):
                    print(f"Item inválido detectado: {item_data}")
                    continue
                
                market_item = MarketItem(snapshot_id=snapshot.id, **item_data)
                session.add(market_item)
                items_added += 1
            except Exception as e:
                print(f"Error procesando item {item_data.get('symbol', 'desconocido')}: {str(e)}")
                continue

        session.commit()
        
        if items_added > 0:
            print(f"Snapshot completado: {items_added} items agregados")
        else:
            print("Advertencia: Snapshot creado pero sin items")
            session.rollback()
            session.delete(snapshot)
            session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error crítico en update_market_snapshot: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        session.close()
