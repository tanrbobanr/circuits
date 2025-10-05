import pytest

from .utils import CellBuilder, register_caps, IN2, IN3
from src.circuits import *


def _not_cell() -> NOT:
    with CellBuilder(NOT) as cell:
        register_caps(cell.i, cell.o)

    return cell


def _nor2_cell() -> NOR2:
    with CellBuilder(NOR2) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _or2_cell() -> OR2:
    with CellBuilder(OR2) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _or3_cell() -> OR3:
    with CellBuilder(OR3) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _nand2_cell() -> NAND2:
    with CellBuilder(NAND2) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _and2_cell() -> AND2:
    with CellBuilder(AND2) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _xor2_cell() -> XOR2:
    with CellBuilder(XOR2) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _xnor2_cell() -> XNOR2:
    with CellBuilder(XNOR2) as cell:
        register_caps(*cell.i, cell.o)

    return cell


def _buf1_cell() -> BUF1:
    with CellBuilder(BUF1) as cell:
        cell.i.register(Cap())
        cell.o.register(Cap(1))

    return cell


def _buf2_cell() -> BUF2:
    with CellBuilder(BUF2) as cell:
        register_caps(*cell.i)
        register_caps(*cell.o, identity=1)

    return cell


not_cell = pytest.fixture(_not_cell)
not_cell_lt = pytest.fixture(scope="session")(_not_cell)
nor2_cell = pytest.fixture(_nor2_cell)
nor2_cell_lt = pytest.fixture(scope="session")(_nor2_cell)
or2_cell = pytest.fixture(_or2_cell)
or2_cell_lt = pytest.fixture(scope="session")(_or2_cell)
or3_cell = pytest.fixture(_or3_cell)
or3_cell_lt = pytest.fixture(scope="session")(_or3_cell)
nand2_cell = pytest.fixture(_nand2_cell)
nand2_cell_lt = pytest.fixture(scope="session")(_nand2_cell)
and2_cell = pytest.fixture(_and2_cell)
and2_cell_lt = pytest.fixture(scope="session")(_and2_cell)
xor2_cell = pytest.fixture(_xor2_cell)
xor2_cell_lt = pytest.fixture(scope="session")(_xor2_cell)
xnor2_cell = pytest.fixture(_xnor2_cell)
xnor2_cell_lt = pytest.fixture(scope="session")(_xnor2_cell)
buf1_cell = pytest.fixture(_buf1_cell)
buf1_cell_lt = pytest.fixture(scope="session")(_buf1_cell)
buf2_cell = pytest.fixture(_buf2_cell)
buf2_cell_lt = pytest.fixture(scope="session")(_buf2_cell)


@pytest.mark.parametrize("i", (False, True))
def test_not(i: bool, not_cell: NOT, not_cell_lt: NOT) -> None:
    # calculate the expected output(s)
    expected = not i

    # set input(s)
    not_cell.i.set_state(Cap, i)
    not_cell_lt.i.set_state(Cap, i)

    # check output(s)
    assert not_cell.o.energized == expected
    assert not_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_nor2(i0: bool, i1: bool, nor2_cell: NOR2, nor2_cell_lt: NOR2) -> None:
    # calculate the expected output(s)
    expected = not (i0 or i1)

    # set input(s)
    for i, v in enumerate((i0, i1)):
        nor2_cell.i[i].set_state(Cap, v)
        nor2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert nor2_cell.o.energized == expected
    assert nor2_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_or2(i0: bool, i1: bool, or2_cell: OR2, or2_cell_lt: OR2) -> None:
    # calculate the expected output(s)
    expected = i0 or i1

    # set input(s)
    for i, v in enumerate((i0, i1)):
        or2_cell.i[i].set_state(Cap, v)
        or2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert or2_cell.o.energized == expected
    assert or2_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1", "i2"), IN3)
def test_or3(
    i0: bool, i1: bool, i2: bool, or3_cell: OR3, or3_cell_lt: OR3
) -> None:
    # calculate the expected output(s)
    expected = i0 or i1 or i2

    # set input(s)
    for i, v in enumerate((i0, i1, i2)):
        or3_cell.i[i].set_state(Cap, v)
        or3_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert or3_cell.o.energized == expected
    assert or3_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_nand2(i0: bool, i1: bool, nand2_cell: NAND2, nand2_cell_lt: NAND2) -> None:
    # calculate the expected output(s)
    expected = not (i0 and i1)

    # set input(s)
    for i, v in enumerate((i0, i1)):
        nand2_cell.i[i].set_state(Cap, v)
        nand2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert nand2_cell.o.energized == expected
    assert nand2_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_and2(i0: bool, i1: bool, and2_cell: AND2, and2_cell_lt: AND2) -> None:
    # calculate the expected output(s)
    expected = i0 and i1

    # set input(s)
    for i, v in enumerate((i0, i1)):
        and2_cell.i[i].set_state(Cap, v)
        and2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert and2_cell.o.energized == expected
    assert and2_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_xor2(i0: bool, i1: bool, xor2_cell: XOR2, xor2_cell_lt: XOR2) -> None:
    # calculate the expected output(s)
    expected = i0 ^ i1

    # set input(s)
    for i, v in enumerate((i0, i1)):
        xor2_cell.i[i].set_state(Cap, v)
        xor2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert xor2_cell.o.energized == expected
    assert xor2_cell_lt.o.energized == expected


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_xnor2(i0: bool, i1: bool, xnor2_cell: XNOR2, xnor2_cell_lt: XNOR2) -> None:
    # calculate the expected output(s)
    expected = not (i0 ^ i1)

    # set input(s)
    for i, v in enumerate((i0, i1)):
        xnor2_cell.i[i].set_state(Cap, v)
        xnor2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert xnor2_cell.o.energized == expected
    assert xnor2_cell_lt.o.energized == expected


@pytest.mark.parametrize("i", (False, True))
def test_buf1(i: bool, buf1_cell: BUF1, buf1_cell_lt: BUF1) -> None:
    # set input(s)
    buf1_cell.i.set_state(Cap, i)
    buf1_cell_lt.i.set_state(Cap, i)

    # check output(s)
    assert buf1_cell.o.energized == i
    assert buf1_cell_lt.o.energized == i


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_buf2(i0: bool, i1: bool, buf2_cell: BUF2, buf2_cell_lt: BUF2) -> None:
    # set input(s)
    for i, v in enumerate((i0, i1)):
        buf2_cell.i[i].set_state(Cap, v)
        buf2_cell_lt.i[i].set_state(Cap, v)

    # check output(s)
    assert buf2_cell.o[0].energized == i0
    assert buf2_cell.o[1].energized == i1
    assert buf2_cell_lt.o[0].energized == i0
    assert buf2_cell_lt.o[1].energized == i1
