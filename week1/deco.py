#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable(fn):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    return fn


def decorator(raw_decorator):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    def better_decorator(fn):
        wrapper = raw_decorator(fn)
        update_wrapper(wrapper, fn)
        return wrapper

    return better_decorator


@decorator
def countcalls(fn):
    '''Decorator that counts calls made to the function decorated.'''
    def wrapper_count(*args, **kwargs):
        wrapper_count.calls += 1
        return fn(*args, **kwargs)
    wrapper_count.calls = 0
    return wrapper_count


@decorator
def memo(fn):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    cached_values = {}

    def wrapper_memo(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cached_values:
            cached_values[key] = fn(*args, **kwargs)
        return cached_values[key]
    return wrapper_memo


@decorator
def n_ary(fn):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def wrapper_nany(*args):
        return reduce(fn, reversed(args))
    return wrapper_nany


def trace(stub='____'):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''
    @decorator
    def trace_decorator(fn):
        def wrapper_trace(*args, **kwargs):
            fn_repr = '{name}({args}{sep}{kwargs})'.format(
                name=fn.__name__,
                args=', '.join(map(str, args)),
                sep=', ' if args and kwargs else '',
                kwargs=', '.join(
                    '{}={}'.format(key, value) for key, value in kwargs.items()
                )
            )
            print '{tab} --> {fn_repr}'.format(
                tab=stub * wrapper_trace.nest_level,
                fn_repr=fn_repr
            )

            wrapper_trace.nest_level += 1
            result = fn(*args, **kwargs)
            wrapper_trace.nest_level -= 1

            print '{tab} <-- {fn_repr} = {res}'.format(
                tab=stub * wrapper_trace.nest_level,
                fn_repr=fn_repr,
                res=result
            )
            return result
        wrapper_trace.nest_level = 0

        return wrapper_trace
    return trace_decorator


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Fib fn."""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print foo(4, 3)
    print foo(4, 3, 2)
    print foo(4, 3)
    print "foo was called", foo.calls, "times"

    print bar(4, 3)
    print bar(4, 3, 2)
    print bar(4, 3, 2, 1)
    print "bar was called", bar.calls, "times"

    print fib.__doc__
    fib(3)
    print fib.calls, 'calls made'


if __name__ == '__main__':
    main()
