from falafel.mappers.httpd import httpd_service_conf
from falafel.tests import context_wrap

HTTPD = """
# Configuration file for the httpd service.

#
# The default processing model (MPM) is the process-based
# 'prefork' model.  A thread-based model, 'worker', is also
# available, but does not work with some modules (such as PHP).
# The service must be stopped before changing this variable.
#
HTTPD=/usr/sbin/httpd.worker

#
# To pass additional options (for instance, -D definitions) to the
# httpd binary at startup, set OPTIONS here.
#
#OPTIONS=

#
# By default, the httpd process is started in the C locale; to
# change the locale in which the server runs, the HTTPD_LANG
# variable can be set.
#
HTTPD_LANG=C
""".strip()


def test_get_httpd():
    context = context_wrap(HTTPD)
    result = httpd_service_conf(context)
    assert result["HTTPD"] == '/usr/sbin/httpd.worker'
    assert result.get("OPTIONS") is None
    assert result['HTTPD_LANG'] == "C"
