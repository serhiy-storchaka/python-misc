from __future__ import print_function
import sys


def test_repr(depth):
    x = None
    for i in range(depth): x = [x]
    repr(x)

def test_eq(depth):
    x = y = None
    for i in range(depth):
        x = [x]
        y = [y]
    x == y

def test_hash(depth):
    x = None
    for i in range(depth): x = (x,)
    hash(x)

def test_filter(depth):
    try:
        from itertools import ifilter
    except ImportError:
        ifilter = filter

    x = iter([1])
    for i in range(depth): x = ifilter(None, x)
    next(x)

def test_map(depth):
    try:
        from itertools import imap
    except ImportError:
        imap = map

    x = iter([True])
    for i in range(depth): x = imap(bool, x)
    next(x)

def test_islice(depth):
    from itertools import islice
    x = iter([1])
    for i in range(depth): x = islice(x, 1)
    next(x)

def test_chain(depth):
    from itertools import chain
    x = iter([1])
    for i in range(depth): x = chain(x)
    next(x)

def test_partial(depth):
    from functools import partial
    x = int
    for i in range(depth):
        x = partial(x, base=2)
        x.x = 1  # prevent collapsing partials
    x('10')

def test_compile(depth):
    x = 'x' + '()' * depth
    compile(x, '?', 'eval')

def test_ast_parse(depth):
    import ast
    x = 'x' + '()' * depth
    ast.parse(x, '?', 'eval')

def test_deepcopy(depth):
    import copy
    x = None
    for i in range(depth): x = [x]
    copy.deepcopy(x)

def test_json_dump(depth):
    import json
    x = None
    for i in range(depth): x = [x]
    json.dumps(x)

def test_json_load(depth):
    import json
    x = '['*depth + 'null' + ']'*depth
    json.loads(x)

def test_pickle_dump(depth):
    try:
        import cPickle as pickle
    except ImportError:
        import pickle

    x = None
    for i in range(depth): x = [x]
    pickle.dumps(x, 2)

# unpickling always is non-recursive?

def test_marshal_dump(depth):
    import marshal
    x = None
    for i in range(depth): x = [x]
    marshal.dumps(x, 2)

def test_marshal_load(depth):
    import marshal
    x = b'[\x01\x00\x00\x00'*depth + b'N'
    marshal.loads(x)

def _test_plistlib_dump(depth):
    try:
        from plistlib import dumps as plistlib_dumps
    except ImportError:
        try:
            from plistlib import writePlistToBytes as plistlib_dumps
        except ImportError:
            from plistlib import writePlistToString as plistlib_dumps

    x = 0
    for i in range(depth): x = [x]
    plistlib_dumps(x)

# non-recursive?
def _test_plistlib_load(depth):
    try:
        from plistlib import loads as plistlib_loads
    except ImportError:
        try:
            from plistlib import readPlistFromBytes as plistlib_loads
        except ImportError:
            from plistlib import readPlistFromString as plistlib_loads

    x = (b'<?xml version="1.0" encoding="UTF-8"?>'
         b'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
         b'"http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
         b'<plist version="1.0">' +
         b'<array>'*depth + b'<integer>0</integer>' + b'</array>'*depth +
         b'</plist>')
    plistlib_loads(x)

def _test_etree_dump(depth):
    try:
        import xml.etree.cElementTree as ElementTree
    except ImportError:
        import xml.etree.ElementTree as ElementTree

    y = x = ElementTree.Element('x')
    for i in range(depth): y = ElementTree.SubElement(y, 'x')
    ElementTree.tostring(x)

# suppose the parsing is non-recursive, but the destructor is
def _test_etree_load(depth):
    try:
        import xml.etree.cElementTree as ElementTree
    except ImportError:
        import xml.etree.ElementTree as ElementTree

    depth += 1
    x = b'<x>'*depth + b'</x>'*depth
    ElementTree.XML(x)

# too slow
def _test_minidom_dump(depth):
    import xml.dom.minidom
    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, 'x', None)
    y = doc.documentElement
    for i in range(depth):
        z = doc.createElement('x')
        y.appendChild(z)
        y = z
    doc.documentElement.toxml()

# non-recursive?
def _test_minidom_load(depth):
    import xml.dom.minidom
    depth += 1
    x = b'<x>'*depth + b'</x>'*depth
    xml.dom.minidom.parseString(x)

def test_python_function(depth):
    def f(n):
        if n: return f(n-1)
    f(depth)

def test_python_method(depth):
    class X:
        def f(self, n):
            if n: return self.f(n-1)
    X().f(depth)

def test_python_iterator(depth):
    class I:
        def __init__(self, it):
            self.it = it
        def __iter__(self):
            return self
        def __next__(self):
            return next(self.it)
        next = __next__
    x = iter([1])
    for i in range(depth): x = I(x)
    next(x)

def test_python_generator(depth):
    x = iter([1])
    for i in range(depth): x = (y for y in x)
    next(x)

if sys.version_info >= (3, 3):
    def test_yield_from(depth):
        ns = {}
        exec('''if True:
            def g(it):
                yield from it
        ''', ns)
        g = ns['g']
        x = iter([1])
        for i in range(depth): x = g(x)
        next(x)

def test_python_call(depth):
    class X:
        def __call__(self, n):
            if n: return self(n-1)
            return 0
    X()(depth)

def test_python_call_keyword(depth):
    class X:
        def __call__(self, n):
            if n: return self(n=n-1)
            return 0
    X()(n=depth)

def test_python_getitem(depth):
    class X:
        def __getitem__(self, n):
            if n: return self[n-1]
            return 0
    X()[depth]

MAX_LIMIT = 300000
if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--run':
        try:
            test = globals()[sys.argv[2]]
            depth = int(sys.argv[3])
            step = int(sys.argv[4])
            sys.setrecursionlimit(MAX_LIMIT + 100)
            while True:
                test(depth)
                print(depth)
                sys.stdout.flush()
                if depth >= MAX_LIMIT:
                    break
                import gc
                gc.collect()
                depth += step
        except (ValueError, RuntimeError):
            sys.exit(1)
        except:
            print('ERROR: %r depth=%d' % (sys.exc_info()[1], depth), file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    import subprocess
    try:
        from time import perf_counter as timer
    except ImportError:
        from time import time as timer

    if len(sys.argv) > 1:
        tests = sys.argv[1:]
        for test in tests:
            if test not in globals():
                sys.exit('no such test: %s' % test)
    else:
        tests = [test for test in sorted(globals()) if test.startswith('test_')]
        #tests = ['test_python_call', 'test_python_getitem', 'test_python_iterator']

    for test in tests:
        try:
            sys.stderr.write('%s ' % (test,))
            sys.stderr.flush()
            start_time = timer()
            step = MAX_LIMIT
            depth = 0
            retry = 0
            while True:
                cmd = [sys.executable, __file__, '--run', test,
                       str(depth + step), str(step)]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                try:
                    for line in process.stdout:
                        new_depth = int(line)
                        depth = max(depth, new_depth)
                        sys.stderr.write('\r%s %s [%.1f]' % (test, depth, timer() - start_time))
                        sys.stderr.flush()
                except:
                    process.kill()
                    raise
                finally:
                    process.stdout.close()
                    process.wait()
                #print('>', test, depth, step, '[%.1f]' % (timer() - start_time), file=sys.stderr)
                if depth >= MAX_LIMIT:
                    depth = 'unlimited'
                    break
                sys.stderr.write('\r%s %s [%.1f]' % (test, depth, timer() - start_time))
                sys.stderr.flush()
                min_step = depth // 1000 if depth > 5000 else 1
                if step < min_step:
                    break
                if step >= 256*min_step:
                    step //= 8
                elif step >= 4*min_step:
                    step //= 4
                elif step > 1:
                    step //= 2
                else:
                    retry += 1
                if retry > 1:
                    break
            sys.stderr.write('\r%s %s [%.1f]\r' % (test, depth, timer() - start_time))
            sys.stderr.flush()
            print(test, depth)
            sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stderr.write('\n')
            sys.stderr.flush()
            print(test, 'interrupted')
            sys.stdout.flush()
