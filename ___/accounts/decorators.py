from functools import wraps
from django.http import HttpResponseForbidden


def leader_or_self_required(view_func):
    """
    Decorator that allows access if:
    - user_id is None (viewing own data)
    - user_id matches request.user.id (viewing own data)
    - request.user is LEADER and target user was referred by them

    Returns 403 Forbidden for unauthorized access attempts.
    """
    @wraps(view_func)
    def _wrapped_view(request, user_id=None, *args, **kwargs):
        from .models import CustomUser

        # Self-access always allowed
        if user_id is None or user_id == request.user.id:
            return view_func(request, user_id, *args, **kwargs)

        # Leader accessing referral
        if request.user.role == CustomUser.Role.LEADER:
            target_user = CustomUser.objects.filter(id=user_id).first()
            if target_user and target_user.referred_by_id == request.user.id:
                return view_func(request, user_id, *args, **kwargs)

        return HttpResponseForbidden("No tienes permiso para esta accion.")
    return _wrapped_view
