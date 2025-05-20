from celery import Celery

celery_app = Celery(
    "nexon_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)


@celery_app.task
def build_package_task(pkg_name, version):
    from nexon_cli.core.build_manager import BuildManager
    return BuildManager().build_package(pkg_name, version)
