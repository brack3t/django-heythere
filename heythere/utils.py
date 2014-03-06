from django.template import Context, Template


def render(template, context):
    tmpl = Template(template)
    ctxt = Context(context)
    return tmpl.render(ctxt)
