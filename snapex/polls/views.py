from django.http import HttpResponse

def index(request):
    import logging
    log = logging.getLogger(__name__)
    log.debug('from debug')
    log.info('from info')
    log.warn('from warn')
    log.error('from error')

    return HttpResponse("Hello, world. You're at the polls index.")