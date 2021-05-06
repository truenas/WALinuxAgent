import platform
import sys
import time
from datetime import datetime


def get_py_major_version():
    return sys.version_info[0]


if get_py_major_version() == 3:
    ustr = str
elif get_py_major_version() == 2:
    ustr = unicode


def str_to_encoded_ustr(s, encoding='utf-8'):
    if get_py_major_version() > 2:
        try:
            # For py3+, str() is unicode by default
            if isinstance(s, bytes):
                # str.encode() returns bytes which should be decoded to get the str.
                return s.decode(encoding)
            else:
                # If its not encoded, just return the string
                return ustr(s)
        except Exception:
            # If some issues in decoding, just return the string
            return ustr(s)
    # For Py2, explicitly convert the string to unicode with the specified encoding
    return ustr(s, encoding=encoding)


def get_current_agent_name(distro_name=None):
    """
    Only Ubuntu and Debian used walinuxagent, everyone else uses waagent.
    Note: If distro_name is not specified, we will search the distro in the VM itself
    :return: walinuxagent or waagent
    """

    if distro_name is None:
        distro_name = platform.linux_distribution()[0]

    walinuxagent_distros = ["ubuntu", "debian"]
    if any(dist.lower() in distro_name.lower() for dist in walinuxagent_distros):
        return "walinuxagent"

    return "waagent"


def execute_with_retry(func, max_retry=3, sleep=5):
    retry = 0
    while retry < max_retry:
        try:
            func()
            return
        except Exception as error:
            print("{0} Op failed with error: {1}. Retry: {2}, total attempts: {3}".format(datetime.utcnow().isoformat(),
                                                                                          error, retry + 1, max_retry))
            retry += 1
            if retry < max_retry:
                time.sleep(sleep)
                continue
            raise

