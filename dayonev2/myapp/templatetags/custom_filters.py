from django import template

register = template.Library()

@register.filter
def multiply_by_25(value):
    return value * 25
