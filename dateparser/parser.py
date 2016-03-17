# coding: utf-8
from cStringIO import StringIO
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta

class _parser(object):

    alpha_directives = OrderedDict([
        ('weekday', ['%A', '%a']),
        ('month', ['%B', '%b']),
    ])

    time_directives = ['%p']

    num_directives = OrderedDict([
        ('month', ['%m']),
        ('day', ['%d']),
        ('year', ['%y', '%Y']),
        ('time', ['%H:%M:%S', '%H:%M', '%I:%M:%S', '%I:%M']),
    ])

    deltas = {
        'pm': timedelta(hours=12),
    }

    def _get_year(self, token):
        for directive in self.num_directives['year']:
            try:
                do = datetime.strptime(token, directive)
                self._token_year = token
                return do.year
            except:
                pass

    def _get_day(self, token):
        for directive in self.num_directives['day']:
            try:
                do = datetime.strptime(token, directive)
                self._token_day = token
                return do.day
            except:
                pass

    def _get_month(self, token):
        for directive in self.num_directives['month']:
            try:
                do = datetime.strptime(token, directive)
                self._token_month = token
                return do.month
            except:
                pass

    def _get_component_token(self, key):
        return getattr(self, '_token_%s' % key, None)

    def __init__(self, tokens, dayfirst=False, yearfirst=False, fuzzy=False, default=None):
        self.day = None
        self.month = None
        self.year = None
        self.time = None
        self.delta = timedelta(0)
        self.default = default

        self.auto_order = []

        self._token_day = None
        self._token_month = None
        self._token_year = None
        self._token_time = None
        self._token_delta = None

        for token, type in tokens:
            if type <= 1:
                results = self._parse(type, token, fuzzy)
                for res in results:
                    setattr(self, *res)

        self.apply_date_order(yearfirst, dayfirst)

    def apply_date_order(self, yearfirst=False, dayfirst=False):
        if not yearfirst and not dayfirst:
            return

        def swap(key1, key2):
            if not(key1 in self.auto_order and key2 in self.auto_order):
                return

            index1 = self.auto_order.index(key1)
            index2 = self.auto_order.index(key2)
            if index1 > index2:
                old_val1, old_val2 = self._get_component_token(key1), \
                    self._get_component_token(key2)

                setattr(self, key1, getattr(self, '_get_%s' % key1)(old_val2))
                setattr(self, key2, getattr(self, '_get_%s' % key2)(old_val1))

                self.auto_order[index1] = key2
                self.auto_order[index2] = key1
        if yearfirst:
            swap('year', 'month')
            swap('month', 'day')

        if dayfirst:
            swap('day', 'month')


    def _get_period(self):
        if 'day' in self.auto_order:
            return 'day'
        elif 'month' in self.auto_order:
            return 'month'
        elif 'year' in self.auto_order:
            return 'year'
        elif 'time' in self.auto_order:
            return 'day'

    def _results(self, complete_partial_dates=True):
        now = None
        if complete_partial_dates:
            now = self.default

        return {
            'day': self.day or getattr(now, 'day'),
            'month': self.month or getattr(now, 'month'),
            'year': self.year or getattr(now, 'year'),
            'hour': getattr(self.time() if self.time else {}, 'hour', None) or getattr(now, 'hour'),
            'minute': getattr(self.time() if self.time else {}, 'minute', None) or getattr(now, 'minute'),
            'second': getattr(self.time() if self.time else {}, 'second', None) or getattr(now, 'second'),
        }

    @classmethod
    def parse(cls, datestring, dayfirst=False, yearfirst=False, fuzzy=False, complete_dates=True, default=datetime.utcnow()):
        tokens = tokenizer(datestring)
        po = cls(tokens.tokenize(), dayfirst, yearfirst, fuzzy, default)
        dateobj = datetime(**po._results(complete_dates))

        if po.delta and po.time().hour <= 12:
            dateobj += po.delta

        return dateobj

    def _parse(self, type, token, fuzzy):

        def set_and_return(token, component, dateobj, skip_date_order=False):
            if not skip_date_order:
                self.auto_order.append(component)
            setattr(self, '_token_%s' % component, token)
            return [(component, getattr(dateobj, component))]

        def parse_number(token):
            for component, directives in self.num_directives.items():
                for directive in directives:
                    try:
                        do = datetime.strptime(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(token, component, do)
                    except:
                        pass
            else:
                raise ValueError('Unable to parse: %s' % token)

        def parse_alpha(token):
            for component, directives in self.alpha_directives.items():
                for directive in directives:
                    try:
                        do = datetime.strptime(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(token, component, do, skip_date_order=True)
                        elif component == 'month':
                            index = self.auto_order.index('month')
                            self.auto_order[index] = 'day'
                            setattr(self, '_token_day', self._token_month)
                            setattr(self, '_token_month', token)
                            return [(component, getattr(do, component)), ('day', prev_value)]
                    except:
                        pass
            else:
                for directive in self.time_directives:
                    try:
                        do = datetime.strptime(token, directive)
                        return [('delta', self.deltas.get(token.lower(), timedelta(0)))]
                    except:
                        pass
                if not fuzzy:
                    raise ValueError('Unable to parse: %s' % token)
                else:
                    return []

        handlers = {0: parse_number, 1: parse_alpha}
        return handlers[type](token)


class tokenizer(object):
    digits = '0123456789:'
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    nonwords = "./\()\"':,.;<>~!@#$%^&*|+=[]{}`~?-     "

    def _isletter(self, x): return x in self.letters
    def _isdigit(self, x): return x in self.digits
    def _isnonword(self, x): return x in self.nonwords

    def __init__(self, ds):
        self.instream = StringIO(ds)

    def _switch(self, chara, charb):
        if self._isdigit(chara):
            return 0, not(self._isdigit(charb))

        if self._isletter(chara):
            return 1, not(self._isletter(charb))

        if self._isnonword(chara):
            return 2, not(self._isnonword(charb))

        return '', True

    def tokenize(self):
        token = ''
        self.EOF = False

        while not self.EOF:
            nextchar = self.instream.read(1)

            if not nextchar:
                self.EOF = True
                type, _ = self._switch(token[-1], nextchar)
                yield token, type
                return

            if token:
                type, switch = self._switch(token[-1], nextchar)

                if not switch:
                    token += nextchar
                else:
                    yield token, type
                    token = nextchar
            else:
                token += nextchar
