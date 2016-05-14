#-*- coding=utf-8 -*-
'''
Provide utility for web applications.
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import get_backends, login, REDIRECT_FIELD_NAME
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import functools
import simplejson as json
from .dj import dj_setting
import time
import datetime


def get_rest_method(req):
    '''
    Get the rest method of request. The function means to get
    the method when browser doesn't support PUT/DELETE http
    methods. So all requests are made by POST/GET, but the
    actual method may be in the _method value from POST query.
    '''
    _m = req.method
    if _m.upper() == 'POST' and '_method' in req.POST:
        _m = req.POST.get('_method').upper()

    return _m


def get_ip(req):
    '''
    Get the real ip address of a request.
    '''
    return req.META.get('HTTP_X_FORWARDED_FOR') or req.META.get('REMOTE_ADDR')


def _protected(req, cache_client=None):
    if not cache_client:
        return
    ip = str(get_ip(req))
    ret = cache_client.incr('protect_%s' % ip, 1)
    if not ret:
        cache_client.set('protect_%s' % ip, 1, 60)
    else:
        if ret > 10000:
            return  HttpResponse(status=403)
        if float(ret) / 60.0 > 0.2:
            cache_client.set('protect_%s' % ip, 10001, 3600)
            return  HttpResponse(status=403)


def _is_mocked(data):
    if hasattr(data, 'get')\
            and data.get('_mock')\
            and dj_setting('DEBUG'):
        return True
    else:
        return False


def _get_mock_response(req, data, template, **kw):
    if template is None:
        return HttpResponse(data.get('_mock'), **kw)
    else:
        return render_to_response(template,
                                  dictionary=json.loads(data.get('_mock')),
                                  context_instance=RequestContext(req))


def _to_response(ret, func, req, template, rest, **kw):
    if not isinstance(ret, HttpResponse):
        if template is not None:
            dictionary = {} if ret is None else ret
            template = dictionary.pop('__template')\
                if '__template' in dictionary else template
            return render_to_response(template,
                                      dictionary=dictionary,
                                      context_instance=RequestContext(req))
        elif isinstance(ret, basestring):
            if 'content_type' not in kw:
                if req.META.get('PATH_INFO', '').endswith('js'):
                    kw['content_type'] = 'application/javascript; charset=utf-8'
                elif req.META.get('PATH_INFO', '').endswith('css'):
                    kw['content_type'] = 'text/css; charset=utf-8'
                else:
                    kw['content_type'] = 'text/plain; charset=utf-8'
        elif isinstance(ret, dict):
            ret = json.dumps(ret)
            if 'content_type' not in kw:
                kw['content_type'] = 'application/json; charset=utf-8'
        elif rest and isinstance(ret, (tuple, list)):
            ret = to_rest_json(ret[0], ret[1])
            if 'content_type' not in kw:
                kw['content_type'] = 'application/json; charset=utf-8'
            else:
                raise Exception("The return of %s.%s can not be handled"
                                % (getattr(func, '__module__', ''),
                                   getattr(func, '__name__', '')))
        ret = HttpResponse(ret, **kw)
    return ret


def _to_log(req, resp, params):
    req_columns = ['REQUEST_METHOD', 'PATH_INFO',
                   'QUERY_STRING', 'HTTP_USER_AGENT', 'HTTP_REFERER']
    ret = ["'%s'" % datetime.datetime.now()]
    ret.append("'%s'" % get_ip(req))
    ret.extend(["'%s'" % req.META.get(col, '') for col in req_columns])
    ret.append("'%s'" % req.COOKIES.get('sessionid', ''))
    ret.append("'%s'" % getattr(req.user, 'id', ''))
    ret.append("'%s'" % len(resp.content))
    ret.append("'%s'" % resp.status_code)
    for param in params:
        ret.append("'%s'" % param)
    return ' '.join(ret)


def get_site_referrer(req):
    ref = req.META.get('HTTP_REFERER', '')
    if ref:
        parsed_ref = urlparse(ref)
        http_host = req.META.get('HTTP_HOST', '')
        if parsed_ref.netloc == http_host:
            return ref
    return None


def redirect_all(to, req=None):
    to_url = to
    if req:
        #if req.META.get('PATH_INFO'):
        #    to_url += req.META.get('PATH_INFO')
        if req.META.get('QUERY_STRING'):
            to_url = '%s?%s' % (to_url,
                                req.META.get('QUERY_STRING'))
    return redirect(to_url)


def hook_before_view(req, **kw):
    pass


def hook_after_view(req, result, **kw):
    pass


def expose(**kw):
    '''
    A decorator for simplifying web controllers, make sure the
    return value from web controllers to be a HttpResponse object.

    Mock suport
    -----------
    If a '_mock' parameter is in the request, the decorator
    will directly return the content of '_mock', or use the
    content as the dictionary of render_to_response when a
    template is specfied. The wrapped function will not be
    executed.

    Parameters
    ----------
    rest: boolean, default False
        Constuct {'status': status_code, ...} like json response.
    template: string, default None
        The template path.
    login_required: boolean, default False
        The view need logined to be accessed. When enabled, if the user
        is not authenticated, and rest is not True, the response will be
        a redirect to the login_url.
    login_url: string, optional
        The login address url, or will use LOGIN_URL if None.
    other parameters in kw:
        The parameters passed to generated HttpResponse object.

    Example
    -------
    @utility.expose(template='xxx/yyy.html')
    def test(req):
        return dict(name='Zhang San')

    @utility.expose(rest=True)
    def resttest(req):
        return 200, dict(content='Nothing')
    Above function will result a json formatted the resposne
    like {"status": 200, "content": "Nothing"}.
    '''
    rest = kw.pop('rest', False)
    template = kw.pop('template', None)
    login_required = kw.pop('login_required', False)
    login_url = kw.pop('login_url', None)
    protected = kw.pop('protected', None)

    def entangle(func):
        @functools.wraps(func)
        def wrapper(req, *sub, **kwargs):
            # Handling request
            data = getattr(req, req.method, {})

            # Handling _mock data
            if _is_mocked(data):
                return _get_mock_response(req, data, template, **kw)
            use_time = time.time()

            # Handling hijacking protection

            forbidden = _protected(req, protected)
            if forbidden:
                return forbidden

            if login_required and not req.user.is_authenticated():
                ret = _set_redirect(req, rest, login_url=login_url,
                                    redirect_field_name=REDIRECT_FIELD_NAME)
            else:
                hook_before_view(req, **kw)
                ret = func(req, *sub, **kwargs)
                hook_after_view(req, ret, **kw)

            # Handling response
            ret = _to_response(ret, func, req, template, rest, **kw)

            use_time = '%4.3f' % (time.time() - use_time)

            # Logging
            # write(_to_log(req, ret, [use_time]), 'access')

            return ret
        wrapper._exposed = True
        wrapper._original = func
        return wrapper
    return entangle


def to_jsonp(callback, data):
    '''
    Convert to jsonp formatted string.
    '''
    return "%s(%s);" % (callback, json.dumps(data))


def to_rest_json(status, data=None):
    ret = {}
    if data:
        ret.update(data)
    ret['status'] = status
    return json.dumps(ret)


def easy_login(req, user):
    backend = get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__,
                              backend.__class__.__name__)
    login(req, user)


class CJsonEncoder(json.JSONEncoder):
    def default(self, datetime):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self.obj)


@expose()
def dummy_web(req, **kw):
    print "URL: %s" % req.build_absolute_uri()
    print "PARAMS: %s" % kw
    return ''


def get_next_url(req, redirect_field_name=REDIRECT_FIELD_NAME):
    '''
    Get the next url from the web request.
    '''
    next_url = getattr(req, req.method).get(REDIRECT_FIELD_NAME, None)\
        or req.COOKIES.get(REDIRECT_FIELD_NAME, None)
    return next_url


def redirect_to_next_url(req, redirect_field_name=REDIRECT_FIELD_NAME,
                         default_url=None):
    '''
    Generate a HttpResponse object redirecting to the next url, and clear
    the related cookies.
    '''
    if default_url is None:
        default_url = '/'
    next_url = get_next_url(req, redirect_field_name=REDIRECT_FIELD_NAME)\
        or default_url
    resp = redirect(next_url)
    resp.delete_cookie(redirect_field_name)
    return resp


def authed(login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    '''
    A decorator to replace django default login_required decorator.
    '''
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()

            resolved_login_url = login_url or dj_setting('LOGIN_URL')

            from django.contrib.auth.views import redirect_to_login
            resp = redirect_to_login(
                path, resolved_login_url, redirect_field_name)

            # Set next url to cookie
            resp.set_cookie(redirect_field_name, path, max_age=7200)
            return resp
        return _wrapped_view
    return decorator


def is_mobile(req):
    '''
    Determine whether the req is issued by a mobile browser.
    '''
    user_agent = req.META.get('HTTP_USER_AGENT', '').lower()
    if 'tablet' in user_agent or 'ipad' in user_agent:
        return False
    if 'mobile' in user_agent or 'android' in user_agent:
        return True
    return False
