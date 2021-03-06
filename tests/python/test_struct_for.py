import taichi as ti


@ti.all_archs
def test_singleton():
    x = ti.var(ti.i32, shape=())

    @ti.kernel
    def fill():
        for I in ti.grouped(x):
            x[I] = 3

    fill()

    assert x[None] == 3


@ti.all_archs
def test_singleton2():
    x = ti.var(ti.i32)

    @ti.layout
    def l():
        ti.root.place(x)

    @ti.kernel
    def fill():
        for I in ti.grouped(x):
            x[I] = 3

    fill()

    assert x[None] == 3


@ti.all_archs
def test_linear():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32)

    n = 128

    @ti.layout
    def place():
        ti.root.dense(ti.i, n).place(x)
        ti.root.dense(ti.i, n).place(y)

    @ti.kernel
    def fill():
        for i in x:
            x[i] = i
            y[i] = i * 2

    fill()

    for i in range(n):
        assert x[i] == i
        assert y[i] == i * 2


@ti.all_archs
def test_nested():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32)

    n = 128

    @ti.layout
    def place():
        ti.root.dense(ti.i, n // 4).dense(ti.i, 4).place(x)
        ti.root.dense(ti.i, n).place(y)

    @ti.kernel
    def fill():
        for i in x:
            x[i] = i
            y[i] = i * 2

    fill()

    for i in range(n):
        assert x[i] == i
        assert y[i] == i * 2


@ti.all_archs
def test_nested2():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32)

    n = 2048

    @ti.layout
    def place():
        ti.root.dense(ti.i, n // 512).dense(ti.i,
                                            16).dense(ti.i,
                                                      8).dense(ti.i,
                                                               4).place(x)
        ti.root.dense(ti.i, n).place(y)

    @ti.kernel
    def fill():
        for i in x:
            x[i] = i
            y[i] = i * 2

    fill()

    for i in range(n):
        assert x[i] == i
        assert y[i] == i * 2


@ti.all_archs
def test_2d():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32)

    n, m = 32, 16

    @ti.layout
    def place():
        ti.root.dense(ti.ij, n).place(x, y)

    @ti.kernel
    def fill():
        for i, j in x:
            x[i, j] = i + j * 2

    fill()

    for i in range(n):
        for j in range(m):
            assert x[i, j] == i + j * 2


@ti.all_archs
def test_2d_non_POT():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32, shape=())

    n, m = 13, 17

    @ti.layout
    def place():
        ti.root.dense(ti.ij, (n, m)).place(x)

    @ti.kernel
    def fill():
        for i, j in x:
            y[None] += i + j * j

    fill()

    tot = 0
    for i in range(n):
        for j in range(m):
            tot += i + j * j
    assert y[None] == tot


@ti.all_archs
def test_nested_2d():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32)

    n = 32

    @ti.layout
    def place():
        ti.root.dense(ti.ij, n // 4).dense(ti.ij, 4).place(x, y)

    @ti.kernel
    def fill():
        for i, j in x:
            x[i, j] = i + j * 2

    fill()

    for i in range(n):
        for j in range(n):
            assert x[i, j] == i + j * 2


@ti.all_archs
def test_nested_2d_more_nests():
    x = ti.var(ti.i32)
    y = ti.var(ti.i32)

    n = 64

    @ti.layout
    def place():
        ti.root.dense(ti.ij, n // 16).dense(ti.ij,
                                            2).dense(ti.ij,
                                                     4).dense(ti.ij,
                                                              2).place(x, y)

    @ti.kernel
    def fill():
        for i, j in x:
            x[i, j] = i + j * 2

    fill()

    for i in range(n):
        for j in range(n):
            assert x[i, j] == i + j * 2


@ti.all_archs
def test_linear_k():
    x = ti.var(ti.i32)

    n = 128

    @ti.layout
    def place():
        ti.root.dense(ti.k, n).place(x)

    @ti.kernel
    def fill():
        for i in x:
            x[i] = i

    fill()

    for i in range(n):
        assert x[i] == i


@ti.all_archs
def test_struct_for_branching():
    # Related issue: https://github.com/taichi-dev/taichi/issues/704
    x = ti.var(dt=ti.i32)
    y = ti.var(dt=ti.i32)
    ti.root.pointer(ti.ij, 128 // 4).dense(ti.ij, 4).place(x, y)

    @ti.kernel
    def func1():
        for i, j in x:
            if x[i, j] & 2 == 2:
                y[i, j] = 1

    @ti.kernel
    def func2():
        for i, j in x:
            if x[i, j] == 2 or x[i, j] == 4:
                y[i, j] = 1

    @ti.kernel
    def func3():
        for i, j in x:
            if x[i, j] & 2 == 2 or x[i, j] & 4 == 4:
                y[i, j] = 1

    func1()
    func2()
    func3()
