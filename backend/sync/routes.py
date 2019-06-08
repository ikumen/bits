import logging

from . import sync_service, bp


log = logging.getLogger(__name__)


@bp.route('/download')
def download():
    sync_service.download()
    return 'OK'