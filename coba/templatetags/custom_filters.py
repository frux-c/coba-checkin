from django import template
from datetime import datetime

register = template.Library()

@register.filter
def str_to_date(value, date_format="%Y-%m-%d"):
    return datetime.strptime(value, date_format).date()

@register.filter
def str_time_to_time(value, time_format="%H:%M:%S.%f"):
    return datetime.strptime(value, time_format).time()

@register.filter
def time_to_str_time(value, time_format="%I:%M %p"):
    return value.strftime(time_format)