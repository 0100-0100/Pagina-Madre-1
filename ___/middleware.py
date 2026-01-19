"""
Custom middleware for global authentication enforcement.
"""

from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware to enforce authentication globally across the site.

    Redirects unauthenticated users to the login page, except for:
    - Login page itself (/login/)
    - Registration page (/register/)
    - Admin pages (/admin/* - admin has its own authentication)
    - Static files (/static/* - needed for login/register page styling)

    Includes ?next= parameter in redirects for post-login navigation.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            path = request.path_info

            # Define URLs that don't require authentication
            open_urls = [
                settings.LOGIN_URL,           # /login/
                reverse('register'),          # /register/ (dynamically resolved)
                '/admin/',                    # Admin has own login
                '/static/',                   # Static files for login/register pages
            ]

            # Check if current path requires authentication
            if not any(path.startswith(url) for url in open_urls):
                # Redirect to login with next parameter for post-login navigation
                return redirect(f'{settings.LOGIN_URL}?next={path}')

        # Continue processing request
        return self.get_response(request)
