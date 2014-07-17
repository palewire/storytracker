#!/usr/bin/env python
import six


class UnicodeMixin(object):
    """
    Mixin class to handle defining the proper __str__/__unicode__
    methods in Python 2 or 3.
    """
    # Python 3
    if six.PY3:
        def __str__(self):
            return self.__unicode__()
    # Python 2
    else:
        def __str__(self):
            return self.__unicode__().encode('utf8')

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__str__())
