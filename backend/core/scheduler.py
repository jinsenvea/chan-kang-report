"""APScheduler 定时任务管理器"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()


def start_scheduler():
    """启动调度器（应用启动时调用）"""
    if not scheduler.running:
        scheduler.start()


def add_cron_job(job_id: str, func, cron_expr: str):
    """添加定时任务"""
    if cron_expr and cron_expr.strip():
        parts = cron_expr.strip().split()
        if len(parts) == 5:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
            )
            scheduler.add_job(func, trigger, id=job_id, replace_existing=True)


def remove_job(job_id: str):
    """移除定时任务"""
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
