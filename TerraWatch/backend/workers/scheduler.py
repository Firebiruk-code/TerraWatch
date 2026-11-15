from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def start_scheduler(sync_fn):
    if not scheduler.running:
        scheduler.add_job(sync_fn, "interval", days=3, id="nisar_3day_sync", replace_existing=True)
        scheduler.start()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()

def get_next_run() -> str:
    job = scheduler.get_job("nisar_3day_sync")
    return str(job.next_run_time) if job else "Every 3 Days"
