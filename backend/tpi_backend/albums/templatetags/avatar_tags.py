from django import template
from django.templatetags.static import static

register = template.Library()

@register.filter
def avatar_url(user):
    """Return the user's avatar URL or default avatar if none exists"""
    if user.avatar and hasattr(user.avatar, 'url'):
        return user.avatar.url
    return static('albums/images/default-avatar.svg')