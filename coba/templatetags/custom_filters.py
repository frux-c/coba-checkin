from django import template
from datetime import datetime

register = template.Library()

@register.filter
def str_to_date(value, date_format="%Y-%m-%d"):
    return datetime.strptime(value, date_format).date()
