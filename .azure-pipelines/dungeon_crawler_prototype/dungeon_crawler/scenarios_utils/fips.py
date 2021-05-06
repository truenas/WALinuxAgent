from __future__ import print_function

import os


def is_fips_enabled():
    fips_enabled = False
    fips_enabled_file = '/proc/sys/crypto/fips_enabled'

    if not os.path.exists(fips_enabled_file):
        print('{0} does not exist'.format(fips_enabled_file))
    else:
        with open(fips_enabled_file) as fh:
            content = fh.readline()
            print('{0} contains: {1}'.format(fips_enabled_file, content))
            fips_enabled = content.startswith('1')
            print('fips enabled: {0}'.format(fips_enabled))
    return fips_enabled
