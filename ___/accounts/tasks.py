"""
Background tasks for the accounts app.

Tasks are executed by Django-Q2 qcluster worker process.
Run worker: python manage.py qcluster
"""
import logging

logger = logging.getLogger('django-q')


def echo_test(message):
    """Simple test task to verify Django-Q2 is working.

    Usage in Django shell:
        from django_q.tasks import async_task
        task_id = async_task('accounts.tasks.echo_test', 'Hello Django-Q2!')
    """
    logger.info(f"Echo task executed: {message}")
    return f"Echo: {message}"
