# -*- coding: utf-8 -*-


class InvalidArgumentError(Exception):
    def __init__(self, name, value, message=''):
        super(InvalidArgumentError, self).__init__('Invalid argument %s: %s; %s' % (name, value, message))
        self.name = name
        self.value = value


class MissingArgumentError(Exception):
    def __init__(self, name, message=''):
        super(MissingArgumentError, self).__init__('Missing parameter %s; %s' % (name, message))
        self.name = name