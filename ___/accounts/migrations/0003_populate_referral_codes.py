from django.db import migrations


def generate_referral_codes(apps, schema_editor):
    """Generate unique referral codes for all existing users."""
    from django.utils.crypto import get_random_string

    CustomUser = apps.get_model('accounts', 'CustomUser')
    existing_codes = set(
        CustomUser.objects.exclude(referral_code__isnull=True)
        .values_list('referral_code', flat=True)
    )

    for user in CustomUser.objects.filter(referral_code__isnull=True):
        while True:
            code = get_random_string(8)
            if code not in existing_codes:
                existing_codes.add(code)
                user.referral_code = code
                user.save(update_fields=['referral_code'])
                break


def reverse_codes(apps, schema_editor):
    """Reverse migration - set all codes to None."""
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.all().update(referral_code=None)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_add_referral_fields'),
    ]

    operations = [
        migrations.RunPython(generate_referral_codes, reverse_codes),
    ]
