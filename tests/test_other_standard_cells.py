import pytest

from .utils import CellBuilder, register_caps, IN2, IN3, IN4
from src.circuits import *


def _half_adder() -> HalfAdder:
    with CellBuilder(HalfAdder) as cell:
        register_caps(*cell.i, cell.s, cell.c)

    return cell


def _full_adder() -> FullAdder:
    with CellBuilder(FullAdder) as cell:
        register_caps(*cell.i, cell.s, cell.cin, cell.cout)

    return cell


def _pg() -> PG:
    with CellBuilder(PG) as cell:
        register_caps(*cell.i, *cell.o)

    return cell


def _pg_cin() -> PGCin:
    with CellBuilder(PGCin) as cell:
        register_caps(*cell.i, *cell.o, cell.cin)

    return cell


def _pg_merge_r2() -> PGMergeR2:
    with CellBuilder(PGMergeR2) as cell:
        register_caps(*cell.i0, *cell.i1, *cell.o)

    return cell


def _pg_half_merge_r2() -> PGHalfMergeR2:
    with CellBuilder(PGHalfMergeR2) as cell:
        register_caps(*cell.i0, cell.i1, cell.o)

    return cell


half_adder = pytest.fixture(_half_adder)
half_adder2 = pytest.fixture(scope="session")(_half_adder)
full_adder = pytest.fixture(_full_adder)
full_adder2 = pytest.fixture(scope="session")(_full_adder)
pg = pytest.fixture(_pg)
pg2 = pytest.fixture(scope="session")(_pg)
pg_cin = pytest.fixture(_pg_cin)
pg_cin2 = pytest.fixture(scope="session")(_pg_cin)
pg_merge_r2 = pytest.fixture(_pg_merge_r2)
pg_merge_r2_2 = pytest.fixture(scope="session")(_pg_merge_r2)
pg_half_merge_r2 = pytest.fixture(_pg_half_merge_r2)
pg_half_merge_r2_2 = pytest.fixture(scope="session")(_pg_half_merge_r2)


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_half_adder(
    i0: bool, i1: bool, half_adder: HalfAdder,
    half_adder2: HalfAdder
) -> None:
    # calculate the expected output(s)
    expected_s = i0 ^ i1
    expected_c = i0 and i1

    # set input(s)
    for i, v in enumerate((i0, i1)):
        half_adder.i[i].set_state(Cap, v)
        half_adder2.i[i].set_state(Cap, v)

    # check output(s)
    assert half_adder.s.energized == expected_s
    assert half_adder.c.energized == expected_c
    assert half_adder2.s.energized == expected_s
    assert half_adder2.c.energized == expected_c


@pytest.mark.parametrize(("i0", "i1", "cin"), IN3)
def test_full_adder(
    i0: bool, i1: bool, cin: bool, full_adder: FullAdder,
    full_adder2: FullAdder
) -> None:
    # calculate the expected output(s)
    expected_s = cin ^ (i0 ^ i1)
    expected_c = (i0 and i1) or (cin and (i0 ^ i1))

    # set input(s)
    for i, v in enumerate((i0, i1)):
        full_adder.i[i].set_state(Cap, v)
        full_adder2.i[i].set_state(Cap, v)

    full_adder.cin.set_state(Cap, cin)
    full_adder2.cin.set_state(Cap, cin)

    # check output(s)
    assert full_adder.s.energized == expected_s
    assert full_adder.cout.energized == expected_c
    assert full_adder2.s.energized == expected_s
    assert full_adder2.cout.energized == expected_c


@pytest.mark.parametrize(("i0", "i1"), IN2)
def test_pg(i0: bool, i1: bool, pg: PG, pg2: PG) -> None:
    # calculate the expected output(s)
    expected_p = i0 ^ i1
    expected_g = i0 and i1

    # set input(s)
    for i, v in enumerate((i0, i1)):
        pg.i[i].set_state(Cap, v)
        pg2.i[i].set_state(Cap, v)

    # check output(s)
    assert pg.o[0].energized == expected_p
    assert pg.o[1].energized == expected_g
    assert pg2.o[0].energized == expected_p
    assert pg2.o[1].energized == expected_g


@pytest.mark.parametrize(("i0", "i1", "cin"), IN3)
def test_pg_cin(
    i0: bool, i1: bool, cin: bool, pg_cin: PGCin, pg_cin2: PGCin
) -> None:
    # calculate the expected output(s)
    ga = i0 and cin
    gb = i1 and cin
    gc = i0 and i1
    expected_p = i0 ^ i1
    expected_g = ga or gb or gc

    # set input(s)
    for i, v in enumerate((i0, i1)):
        pg_cin.i[i].set_state(Cap, v)
        pg_cin2.i[i].set_state(Cap, v)

    pg_cin.cin.set_state(Cap, cin)
    pg_cin2.cin.set_state(Cap, cin)

    # check output(s)
    assert pg_cin.o[0].energized == expected_p
    assert pg_cin.o[1].energized == expected_g
    assert pg_cin2.o[0].energized == expected_p
    assert pg_cin2.o[1].energized == expected_g


@pytest.mark.parametrize(("p0", "g0", "p1", "g1"), IN4)
def test_pg_merge_r2(
    p0: bool, g0: bool, p1: bool, g1: bool, pg_merge_r2: PGMergeR2,
    pg_merge_r2_2: PGMergeR2
) -> None:
    # calculate the expected output(s)
    expected_p = p0 and p1
    expected_g = (p0 and g1) or g0

    # set input(s)
    for i, (pg0, pg1) in enumerate(((p0, p1), (g0, g1))):
        pg_merge_r2.i0[i].set_state(Cap, pg0)
        pg_merge_r2.i1[i].set_state(Cap, pg1)
        pg_merge_r2_2.i0[i].set_state(Cap, pg0)
        pg_merge_r2_2.i1[i].set_state(Cap, pg1)

    # check output(s)
    assert pg_merge_r2.o[0].energized == expected_p
    assert pg_merge_r2.o[1].energized == expected_g
    assert pg_merge_r2_2.o[0].energized == expected_p
    assert pg_merge_r2_2.o[1].energized == expected_g


@pytest.mark.parametrize(("p0", "g0", "g1"), IN3)
def test_pg_half_merge_r2(
    p0: bool, g0: bool, g1: bool, pg_half_merge_r2: PGHalfMergeR2,
    pg_half_merge_r2_2: PGHalfMergeR2
) -> None:
    # calculate the expected output(s)
    expected = g0 or (p0 and g1)

    # set input(s)
    for i, pg in enumerate((p0, g0)):
        pg_half_merge_r2.i0[i].set_state(Cap, pg)
        pg_half_merge_r2_2.i0[i].set_state(Cap, pg)

    pg_half_merge_r2.i1.set_state(Cap, g1)
    pg_half_merge_r2_2.i1.set_state(Cap, g1)

    # check output(s)
    assert pg_half_merge_r2.o.energized == expected
    assert pg_half_merge_r2.o.energized == expected
    assert pg_half_merge_r2_2.o.energized == expected
    assert pg_half_merge_r2_2.o.energized == expected
