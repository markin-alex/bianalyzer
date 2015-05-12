# -*- coding: utf-8 -*-


class InvalidArgumentError(Exception):
    def __init__(self, name, value, message=''):
        super(InvalidArgumentError, self).__init__('Invalid argument %s: %s; %s' % (name, value, message))
        self.name = name
        self.value = value


class MissingParameterError(Exception):
    def __init__(self, name, message=''):
        super(MissingParameterError, self).__init__('Missing parameter %s; %s' % (name, message))
        self.name = name