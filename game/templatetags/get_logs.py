import json
from django import template

register = template.Library()


def parse(value):
    for msg in json.loads(value):
        print(msg)
    return json.loads(value)


register.filter('parse', parse)