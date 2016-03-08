# coding: utf-8
from datetime import datetime

num_directives = [
    ('day', ['%d']),
    ('month', ['%m']),
    ('year', ['%y', '%Y']),
    ('time', ['%H:%M:%S', '%H:%M', '%I:%M:%S', '%I:%M']),
]


alpha_directives = [
    ('weekday', ['%A', '%a']),
    ('month', ['%B', '%b']),
    ('ampm', ['%p']),
]


def iter_directives(ds, designator, directives, result={}):
    for directive in directives:
        try:
            do = datetime.strptime(ds, directive)
            result.update({designator: getattr(do, designator)})
        except:
            pass


class Parser(object):
    directives = {
        0: num_directives,
        1: alpha_directives
    }

    ignore_fields = ['weekday']

    def __init__(self, ds):
        self.orders = {
            'DMY': ['day', 'month', 'year'],
            'MDY': ['month', 'day', 'year'],
            'YMD': ['year', 'month', 'day'],
        }

        self.now = datetime.utcnow()
        self.ds = ds
        self.results = {}
        self.tokens = []
        tkn = tokenizer(ds)

        for token, type in tkn.tokenize():
            self.results[token] = {}
            for dsgn, dtv in self.directives[type]:
                iter_directives(token, dsgn, dtv, self.results[token])
            if not self.results[token]:
                raise ValueError('Unable to parse `%s` in `%s`' % (token, ds))
            self.tokens.append(token)

    def date(self, order='MDY'):
        if order not in self.orders:
            raise ValueError('Unknown date order configuration: %s' % order)

        time_component = self._time()
        date_component = self._date(order)

    def _date(self, order):
        order = self.orders[order]
        dt_kw = {}
        first = order.pop(0)

        while self.tokens:
            token = self.tokens.pop(0)
            if first in self.results[token]:
                dt_kw.update({first: self.results[token][first]})
                first = order.pop(0) if order else ''
                continue

            for kn, kv in self.results[token].items():
                if kn not in dt_kw:
                    if kn in self.ignore_fields:
                        continue
                    dt_kw[kn] = kv
                else:
                    raise ValueError('Too many values for `(%s)` field:' % kn)

        return self.now.replace(**dt_kw)

    def _time(self):
        for token in self.tokens:
            if ':' in token:
                token = self.results.pop(token)
                return token['time']()


class tokenizer(object):
    digits = '0123456789:'
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def _isletter(self, x): return x in self.letters
    def _isdigit(self, x): return x in self.digits

    def __init__(self, ds):
        self.instream = StringIO(ds)

    def _switch(self, chara, charb):
        if not chara:
            return 0, False

        if not charb:
            return '', True

        if self._isdigit(chara):
            return 0, not(self._isdigit(charb))

        if self._isletter(chara):
            return 1, not(self._isletter(charb))

    def tokenize(self):
        token = ''
        self.EOF = False

        while not self.EOF:
            nextchar = self.instream.read(1)

            if not nextchar:
                self.EOF = True

            type, switch = self._switch(token[-1] if token else '', nextchar)
            if not switch:
                type_to_return = type
                token += nextchar
            else:
                yield token, type_to_return
                token = ''
