"""
Background tasks for the accounts app.

Tasks are executed by Django-Q2 qcluster worker process.
Run worker: python manage.py qcluster
"""
import logging
from datetime import timedelta

from django.utils import timezone
from django_q.tasks import schedule

from .models import CedulaInfo, CustomUser
from .scraper import RegistraduriaScraper


logger = logging.getLogger('django-q')

# Backoff delays in seconds: 1min, 5min, 15min
RETRY_DELAYS = [60, 300, 900]
MAX_ATTEMPTS = 3

# Status codes that should NOT trigger retry (permanent results)
PERMANENT_STATUSES = {'found', 'not_found', 'cancelled'}


def echo_test(message):
    """Simple test task to verify Django-Q2 is working.

    Usage in Django shell:
        from django_q.tasks import async_task
        task_id = async_task('accounts.tasks.echo_test', 'Hello Django-Q2!')
    """
    logger.info("Echo task executed: %s", message)
    return f"Echo: {message}"


def validate_cedula(user_id, attempt=1):
    """
    Validate cedula via Registraduria scraper.

    Called by post_save signal on CustomUser creation.
    Implements exponential backoff retry for transient errors.

    Args:
        user_id: CustomUser.id to validate
        attempt: Current attempt number (1-based, max 3)
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        cedula_info = user.cedula_info
    except CustomUser.DoesNotExist:
        logger.error("validate_cedula: User %s not found", user_id)
        return
    except CedulaInfo.DoesNotExist:
        logger.error("validate_cedula: CedulaInfo not found for user %s", user_id)
        return

    # Update status to PROCESSING (browser actively running)
    cedula_info.status = CedulaInfo.Status.PROCESSING
    cedula_info.save(update_fields=['status'])

    logger.info("validate_cedula: User %s (cedula=%s), attempt %d/%d",
                user_id, user.cedula, attempt, MAX_ATTEMPTS)

    # Run scraper
    scraper = RegistraduriaScraper()
    result = scraper.scrape_cedula(user.cedula)

    # Process result based on status
    status = result.get('status')

    if status == 'found':
        _handle_found(cedula_info, result)
    elif status == 'not_found':
        _handle_not_found(cedula_info)
    elif status == 'cancelled':
        _handle_cancelled(cedula_info, result)
    else:
        # Retriable error: timeout, network_error, captcha_failed, parse_error, blocked
        _handle_retriable_error(cedula_info, result, user_id, attempt)


def _handle_found(cedula_info, result):
    """Update CedulaInfo with voting location data."""
    cedula_info.status = CedulaInfo.Status.ACTIVE
    cedula_info.departamento = result.get('departamento') or ''
    cedula_info.municipio = result.get('municipio') or ''
    cedula_info.puesto = result.get('puesto') or ''
    cedula_info.direccion = result.get('direccion') or ''
    cedula_info.mesa = result.get('mesa') or ''
    cedula_info.fetched_at = timezone.now()
    cedula_info.error_message = ''
    cedula_info.save()
    logger.info("validate_cedula: FOUND - %s", cedula_info.user.cedula)


def _handle_not_found(cedula_info):
    """Update CedulaInfo as not found in census."""
    cedula_info.status = CedulaInfo.Status.NOT_FOUND
    cedula_info.fetched_at = timezone.now()
    cedula_info.error_message = ''
    cedula_info.save()
    logger.info("validate_cedula: NOT_FOUND - %s", cedula_info.user.cedula)


def _handle_cancelled(cedula_info, result):
    """Update CedulaInfo with cancelled cedula data."""
    # Determine if deceased or other cancellation
    novedad = result.get('novedad') or ''
    if 'FALLECIDO' in novedad.upper() or 'MUERTE' in novedad.upper():
        cedula_info.status = CedulaInfo.Status.CANCELLED_DECEASED
    else:
        cedula_info.status = CedulaInfo.Status.CANCELLED_OTHER

    cedula_info.novedad = novedad
    cedula_info.resolucion = result.get('resolucion') or ''
    cedula_info.fecha_novedad = result.get('fecha_novedad') or ''
    cedula_info.fetched_at = timezone.now()
    cedula_info.error_message = ''
    cedula_info.save()
    logger.info("validate_cedula: CANCELLED - %s", cedula_info.user.cedula)


def _handle_retriable_error(cedula_info, result, user_id, attempt):
    """Handle retriable error: schedule retry or mark as final error."""
    error_status = result.get('status', 'error')
    error_msg = result.get('error', 'Unknown error')

    if attempt < MAX_ATTEMPTS:
        # Schedule retry with exponential backoff
        delay_seconds = RETRY_DELAYS[attempt - 1]  # 0-indexed: [60, 300, 900]
        next_run = timezone.now() + timedelta(seconds=delay_seconds)

        # Update status and retry count
        cedula_info.retry_count = attempt
        cedula_info.error_message = f"Attempt {attempt}: {error_status} - {error_msg}"
        cedula_info.save(update_fields=['retry_count', 'error_message'])

        logger.warning(
            "validate_cedula: %s on attempt %d, scheduling retry in %ds for user %s",
            error_status, attempt, delay_seconds, user_id
        )

        # Schedule delayed retry using Django-Q2 schedule()
        schedule(
            'accounts.tasks.validate_cedula',
            user_id,
            attempt + 1,
            schedule_type='O',  # Once (one-time execution)
            next_run=next_run,
            name=f'validate_cedula_retry_{user_id}_{attempt + 1}'
        )
    else:
        # Max attempts exhausted - set final error status
        _mark_as_error(cedula_info, error_status, error_msg, result.get('raw_html'))


def _mark_as_error(cedula_info, error_status, error_msg, raw_html=None):
    """Mark CedulaInfo as ERROR after all retries exhausted."""
    # Map scraper status to CedulaInfo.Status
    if error_status == 'timeout':
        cedula_info.status = CedulaInfo.Status.TIMEOUT
    elif error_status == 'blocked':
        cedula_info.status = CedulaInfo.Status.BLOCKED
    else:
        cedula_info.status = CedulaInfo.Status.ERROR

    cedula_info.retry_count = MAX_ATTEMPTS
    cedula_info.error_message = f"After {MAX_ATTEMPTS} attempts: {error_msg}"
    cedula_info.fetched_at = timezone.now()
    if raw_html:
        cedula_info.raw_response = raw_html
    cedula_info.save()
    logger.error("validate_cedula: ERROR after max attempts - %s",
                 cedula_info.user.cedula)
