from django.utils.translation import get_language


def localized(ne_value, en_value):
    return ne_value if get_language() == 'ne' else en_value
