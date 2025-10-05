import random
from typing import Union, TypeVar

import pytest

from .utils import register_caps
from src.circuits import *


_KSA = TypeVar("_KSA", bound=Union[KSA16R2Cin, KSA32R2Cin, KSA64R2Cin])


def _ksa(tp: type[_KSA]) -> tuple[
    _KSA, SignalInterface, SignalInterface, SignalInterface
]:
    vdd = VDD()
    ksa = tp(vdd)
    register_caps(ksa.cin, ksa.cout)
    out = (
        ksa,
        SignalInterface(ksa.i0),
        SignalInterface(ksa.i1),
        SignalInterface(ksa.o),
    )
    vdd.energize()

    return out
    


@pytest.fixture(scope="session")
def ksa_16r2() -> tuple[
    KSA16R2Cin, SignalInterface, SignalInterface, SignalInterface
]:
    return _ksa(KSA16R2Cin)


@pytest.fixture(scope="session")
def ksa_32r2() -> tuple[
    KSA32R2Cin, SignalInterface, SignalInterface, SignalInterface
]:
    return _ksa(KSA32R2Cin)


@pytest.fixture(scope="session")
def ksa_64r2() -> tuple[
    KSA64R2Cin, SignalInterface, SignalInterface, SignalInterface
]:
    return _ksa(KSA64R2Cin)


@pytest.mark.parametrize(
    ("i0", "i1", "cin"),
    zip(
        (random.randint(0, (1 << 16) - 1) for _ in range(250)),
        (random.randint(0, (1 << 16) - 1) for _ in range(250)),
        (random.randint(0, 1) for _ in range(250))
    )
)
def test_ksa_16r2(
    i0: int, i1: int, cin: int,
    ksa_16r2: tuple[KSA16R2Cin, SignalInterface, SignalInterface, SignalInterface]
) -> None:
    # calculate the expected output(s)
    total = i0 + i1 + cin
    expected_o = total & ((1 << 16) - 1)
    expected_cout = not not (total >> 16)

    # set input(s)
    ksa_16r2[0].cin.set_state(Cap, not not cin)
    ksa_16r2[1].set_signal(i0)
    ksa_16r2[2].set_signal(i1)

    # check output(s)
    assert ksa_16r2[3].get_signal() == expected_o
    assert ksa_16r2[0].cout.energized == expected_cout


@pytest.mark.parametrize(
    ("i0", "i1", "cin"),
    zip(
        (random.randint(0, (1 << 32) - 1) for _ in range(250)),
        (random.randint(0, (1 << 32) - 1) for _ in range(250)),
        (random.randint(0, 1) for _ in range(250))
    )
)
def test_ksa_32r2(
    i0: int, i1: int, cin: int,
    ksa_32r2: tuple[KSA32R2Cin, SignalInterface, SignalInterface, SignalInterface]
) -> None:
    # calculate the expected output(s)
    total = i0 + i1 + cin
    expected_o = total & ((1 << 32) - 1)
    expected_cout = not not (total >> 32)

    # set input(s)
    ksa_32r2[0].cin.set_state(Cap, not not cin)
    ksa_32r2[1].set_signal(i0)
    ksa_32r2[2].set_signal(i1)

    # check output(s)
    assert ksa_32r2[3].get_signal() == expected_o
    assert ksa_32r2[0].cout.energized == expected_cout


@pytest.mark.parametrize(
    ("i0", "i1", "cin"),
    zip(
        (random.randint(0, (1 << 64) - 1) for _ in range(250)),
        (random.randint(0, (1 << 64) - 1) for _ in range(250)),
        (random.randint(0, 1) for _ in range(250))
    )
)
def test_ksa_64r2(
    i0: int, i1: int, cin: int,
    ksa_64r2: tuple[KSA64R2Cin, SignalInterface, SignalInterface, SignalInterface]
) -> None:
    # calculate the expected output(s)
    total = i0 + i1 + cin
    expected_o = total & ((1 << 64) - 1)
    expected_cout = not not (total >> 64)

    # set input(s)
    ksa_64r2[0].cin.set_state(Cap, not not cin)
    ksa_64r2[1].set_signal(i0)
    ksa_64r2[2].set_signal(i1)

    # check output(s)
    assert ksa_64r2[3].get_signal() == expected_o
    assert ksa_64r2[0].cout.energized == expected_cout
