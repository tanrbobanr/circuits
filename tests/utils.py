import itertools
from typing import TypeVar, Any, Generic, Union

from src.circuits import Cell, VDD, Via, Cap


IN2 = tuple(itertools.product((False, True), (False, True)))
IN3 = tuple(itertools.product((False, True), (False, True), (False, True)))
IN4 = tuple(itertools.product(
    (False, True), (False, True), (False, True), (False, True)
))


_SC = TypeVar("_SC", bound=Cell)


class CellBuilder(Generic[_SC]):
    def __init__(self, cell_type: type[_SC]) -> None:
        self.vdd = VDD()
        self.cell = cell_type(self.vdd)

    def __enter__(self) -> _SC:
        return self.cell

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.vdd.energize()


def register_caps(*vias: Via, identity: Union[Any, None] = None) -> None:
    for v in vias:
        v.register(Cap(identity))
