import os
from jinja2 import Template
import json

def render_template(template_str, context):
    if not isinstance(template_str, str):
        return template_str
    # Filter context to only include valid Python identifier keys (strings that are valid variable names)
    # This is needed because **kwargs requires string keys that are valid Python identifiers
    filtered_context = {
        k: v for k, v in context.items() 
        if isinstance(k, str) and k.isidentifier()
    }
    # Pass context as both expanded kwargs AND as _context dict for dynamic key access
    return Template(template_str).render(_context=context, **filtered_context)


def load_external_file_if_needed(value, context):
    if isinstance(value, str) and os.path.isfile(value):
        try:
            with open(value, 'r') as f:
                try:
                    return json.load(f)
                except Exception:
                    f.seek(0)
                    return f.read()
        except Exception:
            return value
    return value


def render_hybrid(value, context):
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            rv = render_hybrid(v, context)
            if isinstance(rv, str) and rv.lower() in ["true", "false"]:
                result[k] = rv.lower() == "true"
            elif isinstance(rv, str) and rv.isdigit():
                result[k] = int(rv)
            else:
                result[k] = rv
        return result
    elif isinstance(value, list):
        return [render_hybrid(item, context) for item in value]
    elif isinstance(value, str):
        rendered = render_template(value, context)
        loaded = load_external_file_if_needed(rendered, context)
        return loaded if loaded != rendered else rendered
    return value
