"""
Signals for the accounts app.

Signal handlers are registered in AccountsConfig.ready() via import.
"""
import logging
from functools import partial

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from .models import CedulaInfo, CustomUser


logger = logging.getLogger('django-q')


@receiver(post_save, sender=CustomUser, dispatch_uid='queue_cedula_validation')
def queue_cedula_validation(sender, instance, created, raw, **kwargs):
    """
    Queue cedula validation task when new user is created.

    Uses transaction.on_commit() to ensure task is queued only after
    the user registration transaction successfully commits.

    Args:
        sender: CustomUser model class
        instance: The saved CustomUser instance
        created: True if new user, False if update
        raw: True if loading fixtures
    """
    if not created:
        return  # Only trigger on new user creation

    if raw:
        return  # Skip when loading fixtures

    # Create CedulaInfo record with PENDING status
    # This happens inside the transaction
    CedulaInfo.objects.create(
        user=instance,
        status=CedulaInfo.Status.PENDING,
        retry_count=0
    )

    logger.info("CedulaInfo created for user %s (id=%s), registering on_commit callback",
                instance.cedula, instance.id)

    # Queue async task AFTER transaction commits
    # Using partial to pass user_id
    transaction.on_commit(
        partial(_queue_validation_task, instance.id),
        using='default'
    )
    logger.debug("on_commit callback registered for user_id=%s", instance.id)


def _queue_validation_task(user_id):
    """
    Helper function to queue the validation task.

    Called by on_commit after transaction commits successfully.
    """
    logger.info("on_commit callback fired for user_id=%s, attempting to queue task", user_id)
    try:
        task_id = async_task(
            'accounts.tasks.validate_cedula',
            user_id,
            task_name=f'validate_cedula_{user_id}'
        )
        logger.info("Queued validate_cedula task %s for user_id=%s", task_id, user_id)
    except Exception as e:
        logger.error("Failed to queue validate_cedula for user_id=%s: %s", user_id, e, exc_info=True)
