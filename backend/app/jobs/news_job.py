from app.services.news_service import run_update_logic


def update_news_job():
    run_update_logic("tecnologia")
    run_update_logic("negocios")
