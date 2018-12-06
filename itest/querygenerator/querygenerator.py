import os
import sys


class QueryGenerator(list):

    def __init__(self, grammar, maps={}):
        self.grammar = grammar
        self.ignores = maps.get('replace_map', {})
        self.max_repeat_n_map = maps.get('max_repeat_n_map', {})
        self.max_list_n_map = maps.get('max_list_n_map', {})
        self.default_list_n = maps.get('default_list_n', 1)
        self.regex_map = maps.get('regex_map', {})

    def generate_queries(self, ename='START'):
        try:
            ele = getattr(self.grammar, ename)
        except AttributeError:
            print('{} element niet gevonden in tree'.format(ename))
        else:
            for q in self._addq([ele]):
                yield ' '.join(map(str, q)).strip()

    def _addq(self, q):
        for i, e in enumerate(q):
            if isinstance(e, str) or isinstance(e, int) or \
                    isinstance(e, float):
                continue

            ename = getattr(e, 'name', None)
            iv = self.ignores.get(ename)
            if iv is not None:
                q[i] = iv
                break

            self.append(ename)
            for q1 in getattr(self, '_on_'+e.__class__.__name__)(q, i):
                for q2 in self._addq(q1):
                    yield q2
            self.pop()
            q[i] = e
            break
        else:
            yield q

    def _on_Keyword(self, q, i):
        q[i] = q[i]._keyword
        yield q

    def _on_Regex(self, q, i):
        re_map = self.regex_map[self[-1]]
        for ename in self[::-1]:
            val = re_map.get(ename)
            if val is not None:
                q[i] = val
                break
        else:
            print('geen waarde gevonden voor:')
            print(self[-1])
            print(q[:i+1])
            print(i, len(self), self)
            print(self.regex_map)
            assert 0

        yield q

    def _on_Token(self, q, i):
        q[i] = q[i]._token
        yield q

    def _on_Tokens(self, q, i):
        for e1 in q[i]._tokens:
            q[i] = e1
            yield q

    def _on_Sequence(self, q, i):
        q = q[:i]+q[i]._elements+q[i+1:]
        yield q

    def _on_List(self, q, i):
        if q[i]._min == 0:
            q0 = q[:i]+q[i+1:]
            yield q0

        if q[i]._max == 1:
            q0 = q[:i]+list(q[i]._elements)[:1]+q[i+1:]
            yield q0
        else:
            name = getattr(q[i], 'name', getattr(q[i]._element, 'name', None))
            n = self.max_list_n_map.get(name, self.default_list_n)
            # print(n, getattr(q[i], 'name', None))
            if q[i]._max:
                n = min(n, q[i]._max)

            eles = list(q[i]._elements)[:1] + \
                [q[i]._delimiter, list(q[i]._elements)[0]]*(n-1)
            # if getattr(q[i]._delimiter, '_token', None) == ',':
            #    eles = list(q[i]._elements)[:1] + \
            #    [q[i]._delimiter,
            #    list(q[i]._elements)[0]]*(self.max_list_n_simple-1)
            # else:
            #    eles = list(q[i]._elements)[:1]+[q[i]._delimiter,
            # list(q[i]._elements)[0]]*(self.max_list_n-1)
            q0 = q[:i]+eles+q[i+1:]
            yield q0

    def _on_Repeat(self, q, i):
        if q[i]._min == 0:
            q0 = q[:i]+q[i+1:]
            yield q0

        if q[i]._max == 1:
            q0 = q[:i]+list(q[i]._elements)[:1]+q[i+1:]
            yield q0
        else:
            n = self.max_repeat_n_map.get(getattr(q[i], 'name', None), 1)
            eles = list(q[i]._elements)[:1]*n
            q0 = q[:i]+eles+q[i+1:]
            yield q0

    def _on_Optional(self, q, i):
        q[i] = list(q[i]._elements)[0]
        yield q
        q[i] = ''
        yield q

    def _on_Choice(self, q, i):
        for e1 in q[i]._elements:
            q[i] = e1
            yield q

    def _on_Rule(self, q, i):
        for e1 in q[i]._element._elements:
            if e1.__class__.__name__ == 'Sequence' and sum(
                    e2.__class__.__name__ == 'This' for e2 in e1._elements):
                continue

            q[i] = e1
            yield q

    def _on_This(self, q, i):
        pass


if __name__ == '__main__':
    import sys
    from k_map import k_map
    sys.path.append('../../grammar/')
    from pygrammar.grammar import SiriGrammar  # nopep8

    qb = Querybouwer({
        'regex_map': k_map,
        'max_list_n_map': {
            'series_match': 1,
            'aggregate_functions': 1,
            'select_aggregate': 1
        },
        'default_list_n': 2,
        'replace_map': {
            'k_prefix': '',
            'k_suffix': '',
            'k_where': '',
            'after_expr': '',
            'before_expr': '',
            'between_expr': '',
            'k_merge': '',
            'r_singleq_str': '',

            # 'f_median': '',
            # 'f_median_low': '',
            # 'f_median_high': '',
            'k_now': '',
            'r_float': '',
            'r_time_str': '',
            # 'r_grave_str': '',
            # 'f_filter': '',
            }
        })

    maps = {
        'replace_map': {
            'select_stmt': '',
            # 'list_stmt': '',
            # 'count_stmt': '',
            # 'drop_stmt': '',
            # 'alter_stmt': '',
            # 'create_stmt': '',
            # 'revoke_stmt': '',
            # 'grant_stmt': '',
            # 'show_stmt': '',
            'calc_stmt': '',

            # 'k_prefix': '',
            # 'k_suffix': '',
            # 'k_where': '',
            # 'after_expr': '',
            # 'before_expr': '',
            # 'between_expr': '',
            # 'k_merge': '',
            # 'k_limit': '',
            # 'k_timeit': '',
            'r_comment': '',
            'r_singleq_str': '',
        }, 'regex_map': k_map,
    }

    qb = Querybouwer(SiriGrammar, maps)
    for q in qb.generate_queries(base_ele):
        print(q)