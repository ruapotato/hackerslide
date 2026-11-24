"""Minimal S-expression reader/writer for KiCad files (symbols, schematics).

Strings that were quoted in the source stay quoted when written back (class Q).
"""


class Q(str):
    """A quoted string atom."""


def parse(text):
    pos = 0
    n = len(text)
    stack = [[]]
    while pos < n:
        c = text[pos]
        if c in ' \t\r\n':
            pos += 1
        elif c == '(':
            stack.append([])
            pos += 1
        elif c == ')':
            node = stack.pop()
            stack[-1].append(node)
            pos += 1
        elif c == '"':
            pos += 1
            buf = []
            while True:
                c = text[pos]
                if c == '\\':
                    nxt = text[pos + 1]
                    buf.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(nxt, '\\' + nxt))
                    pos += 2
                elif c == '"':
                    pos += 1
                    break
                else:
                    buf.append(c)
                    pos += 1
            stack[-1].append(Q(''.join(buf)))
        else:
            start = pos
            while pos < n and text[pos] not in ' \t\r\n()':
                pos += 1
            stack[-1].append(text[start:pos])
    assert len(stack) == 1, 'unbalanced parens'
    return stack[0][0] if len(stack[0]) == 1 else stack[0]


def quote(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def dump(node, indent=0):
    """Serialize a parsed node. Short lists stay on one line."""
    if isinstance(node, Q):
        return quote(node)
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float)):
        return fmt(node)
    parts = [dump(x, indent + 1) for x in node]
    one = '(' + ' '.join(parts) + ')'
    if len(one) < 100 and '\n' not in one:
        return one
    pad = '\t' * (indent + 1)
    return '(' + parts[0] + ''.join('\n' + pad + p for p in parts[1:]) + '\n' + '\t' * indent + ')'


def fmt(v):
    if isinstance(v, float):
        s = ('%.4f' % v).rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    return str(v)


def find(node, key):
    """First child list whose head is key."""
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def findall(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]
