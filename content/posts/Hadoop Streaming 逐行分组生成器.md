---
title: "Hadoop Streaming 逐行分组代码片段(生成器版)"
date: 2022-03-14T23:53:36+08:00
description: ""
categories: Python
draft: false
---

1. 为什么要用生成器
   
   1. 省内存
      
      1. 每次只处理一行, 但是做好了分组, 不需要每组一次读入内存
   
   2. 转列表也很方便
      
      1. 生成器只需要 list(generator) 就可以转列表

2. 不废话上代码, 主要手段就是 **闭包+生成器**

```python
import sys


def get_windows(lines=sys.stdin, sep='\t'):
    # hadoop streaming: split stdin into groups

    def iter_lines(lines=sys.stdin, sep='\t'):
        current_key = None
        for line in lines:
            key, line = line.split(sep, 1)
            if key is not current_key:
                yield ...
                current_key = key
            yield (key, line)

    has_more = None
    last_generator = None
    gen = iter_lines(lines=lines, sep=sep)

    def window_iter():
        nonlocal has_more
        while 1:
            try:
                line = next(gen)
                if line is ...:
                    if has_more is None:
                        has_more = True
                        continue
                    else:
                        break
                else:
                    yield line
            except StopIteration:
                has_more = False
                break

    while has_more is not False:
        if last_generator:
            try:
                next(last_generator)
                raise RuntimeError('last generator has not been used up')
            except StopIteration:
                pass
        last_generator = window_iter()
        yield last_generator


def test():
    lines = '''a\t1\na\t1\nb\t2\nb\t2\nb\t2\n'''.strip().splitlines()
    assert [list(i) for i in get_windows(lines)] == [[('a', '1'), ('a', '1')],
                                                     [('b', '2'), ('b', '2'),
                                                      ('b', '2')]]
    for gen in get_windows(lines):
        for i in gen:
            print(i)
    for gen in get_windows(lines):
        line_group = list(gen)
        print(line_group)


if __name__ == "__main__":
    test()

```
