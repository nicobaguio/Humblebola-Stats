from django import template
from humblebola.models import *

register = template.Library()


@register.simple_tag
def link_to_sns(string, sns):
    sns_choices = ['twitter', 'facebook']
    if sns.lower() in sns_choices:
        if sns.lower() == 'twitter':
            return "https://{}.com/{}".format(sns.lower(), string)
        elif sns.lower() == 'facebook':
            return "https://{}.com/{}".format(sns.lower(), string)
    else:
        raise template.TemplateSyntaxError("wrong format.")
