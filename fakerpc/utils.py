from flask import Response
from functools import wraps

def returns_xml(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type="text/xml; charset=utf-8")

    return decorated_function

def parse_bool(s):
    s = s.lower()
    if s in ('true', 't', '1'): return True
    if s in ('false', 'f', '0'): return False
    
    raise ValueError("not a valid boolean string: " + s)

