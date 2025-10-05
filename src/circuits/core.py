from __future__ import annotations
import dataclasses
import operator
from typing import *


__all__ = (
    "Components",
    "TempComponents",
    "Cell",
    "StateEffector",
    "Cap",
    "Via",
    "Binding",
    "Via2",
    "Via4",
    "Via8",
    "Via16",
    "Via32",
    "Via64",
    "VDD",
    "Interconnect",
    "FinFET",
    "PTypeFinFET",
    "SignalInterface",
)


@dataclasses.dataclass(eq=False, frozen=True, slots=True)
class Components:
    cells: tuple[Cell, ...]
    vias: tuple[Via, ...]
    interconnects: tuple[Interconnect, ...]
    bindings: tuple[Binding, ...]

    def all_cells(self) -> Generator[Cell, None, None]:
        yield from self.cells

        for c in self.cells:
            yield from c.components.all_cells()

    def all_vias(self) -> Generator[Via, None, None]:
        yield from self.vias

        for c in self.cells:
            yield from c.components.all_vias()

    def all_interconnects(self) -> Generator[Via, None, None]:
        yield from self.interconnects

        for c in self.cells:
            yield from c.components.all_interconnects()

    def all_bindings(self) -> Generator[Via, None, None]:
        yield from self.bindings

        for c in self.cells:
            yield from c.components.all_bindings()

    def num_cells(self) -> int:
        return len(set(map(id, self.all_cells())))

    def num_vias(self) -> int:
        return len(set(map(id, self.all_vias())))

    def num_interconnects(self) -> int:
        return len(set(map(id, self.all_interconnects())))

    def num_bindings(self) -> int:
        return len(set(map(id, self.all_bindings())))


@dataclasses.dataclass(eq=False, slots=True)
class TempComponents:
    cells: list[Cell] = dataclasses.field(default_factory=list)
    vias: list[Via] = dataclasses.field(default_factory=list)
    interconnects: list[Interconnect] = dataclasses.field(default_factory=list)
    bindings: list[Binding] = dataclasses.field(default_factory=list)

    def add(
        self, *components: Union[Via, Interconnect, Binding, Cell]
    ) -> None:
        for c in components:
            if isinstance(c, Via):
                self.vias.append(c)
            elif isinstance(c, Interconnect):
                self.interconnects.append(c)
            elif isinstance(c, Binding):
                self.bindings.append(c)
            elif isinstance(c, Cell):
                self.cells.append(c)

    def to_components(self) -> Components:
        return Components(
            cells=tuple(self.cells),
            vias=tuple(self.vias),
            interconnects=tuple(self.interconnects),
            bindings=tuple(self.bindings)
        )


class Cell:
    __slots__ = ("components",)

    components: Components

    def __repr__(self) -> str:
        args = " ".join(
            f"{k}={getattr(self, k)!r}" for k in self.__slots__
            if k != "components"
        )
        return f"{type(self).__name__}[{args}]"

    def __init__(self, vdd: VDD) -> None:
        if vdd.energized:
            raise ValueError(
                "Cannot create a component using an energized power rail"
            )
        self._init(vdd)

    def _init(self, vdd: VDD) -> None:
        raise NotImplementedError


class StateEffector:
    __slots__ = ("id", "callback", "energized")

    id: int
    callback: Callable[[Via, bool], None]
    energized: bool

    def __init__(
        self, identity: Any, callback: Callable[[Via, bool], None]
    ) -> None:
        object.__setattr__(self, "id", id(identity))
        object.__setattr__(self, "callback", callback)
        object.__setattr__(self, "energized", False)

    def set_state(self, energized: bool, /) -> bool:
        if self.energized is energized:
            return False
        object.__setattr__(self, "energized", energized)
        return True

    def __setattr__(self, name: str, value: Any, /) -> None:
        raise AttributeError(
            "This object does not support attribute assignment"
        )


class Cap(StateEffector):
    def __init__(self, identity: Union[Any, None] = None) -> None:
        super().__init__(
            type(self) if identity is None else identity, self._callback
        )

    def _callback(self, via: Via, state_changed: bool, /) -> None:
        return


class Via:
    def __init__(self) -> None:
        self.effectors: dict[int, StateEffector] = dict()
        self.opposing_effectors: dict[int, StateEffector] = dict()

    def __repr__(self) -> str:
        effectors = tuple(
            str(int(a.energized)) for a in self.effectors.values()
        ) + ("?", "?")
        return f"{type(self).__name__}[{effectors[0]} {effectors[1]}]"

    def register(self, effector: StateEffector) -> None:
        if not self.effectors:
            self.effectors[effector.id] = effector
            return

        if len(self.effectors) > 1:
            raise ValueError("This via already has two state pairs registered")

        if effector.id in self.effectors:
            raise ValueError("This state effector is already registered")

        if effector.energized:
            raise ValueError("Cannot connect an energized state effector")

        # add second effector and build the opposing effectors dict
        self.effectors[effector.id] = effector
        a0 = next(iter(self.effectors.values()))
        self.opposing_effectors = {effector.id: a0, a0.id: effector}

    def set_state(self, identity: Any, state: bool, /) -> None:
        id_ = id(identity)
        a0 = self.effectors[id_]

        # if we only have one effector, we don't need to deal with
        # callbacks
        if not self.opposing_effectors:
            a0.set_state(state)
            return

        a1 = self.opposing_effectors[id_]
        was_double_off = not (a0.energized or a1.energized)

        if a0.set_state(state):
            state_changed = was_double_off or not (state or a1.energized)
            a1.callback(self, state_changed)

    @property
    def energized(self) -> bool:
        return any(map(
            operator.attrgetter("energized"), self.effectors.values()
        ))

    def get_se(self, identity: Any, /) -> StateEffector:
        return self.effectors[id(identity)]

    def get_ose(self, identity: Any, /) -> StateEffector:
        return self.opposing_effectors[id(identity)]


class Binding(StateEffector):
    __slots__ = ("vias", "num_energized")

    vias: tuple[Via, Via]
    num_energized: Literal[0, 1, 2]

    def __init__(self, a: Via, b: Via, /) -> None:
        for v in (a, b):
            v.register(self._create_state_effector())

            if v.opposing_effectors and v.get_ose(self).energized:
                raise ValueError("Cannot interconnect an energized via")

        object.__setattr__(self, "vias", (a, b))
        object.__setattr__(self, "num_energized", 0)

    @classmethod
    def parallel(
        cls, a: Iterable[Via], b: Iterable[Via], /
    ) -> tuple[Self, ...]:
        a, b = tuple(a), tuple(b)
        assert len(a) == len(b)
        return tuple(cls(*pair) for pair in zip(a, b))

    def __repr__(self) -> str:
        return f"{type(self).__name__}[vias={self.vias!r}]"

    def __setattr__(self, name: str, value: Any, /) -> None:
        raise AttributeError(
            "This object does not support attribute assignment"
        )

    def _create_state_effector(self) -> StateEffector:
        return StateEffector(self, self._handle_state_change)

    def _set_num_energized(self, num_energized: int, /) -> None:
        object.__setattr__(self, "num_energized", num_energized)

    def _get_other_via(self, via: Via) -> Via:
        return self.vias[not self.vias.index(via)]

    def _handle_state_change(self, via: Via, state_changed: bool, /) -> None:
        num_energized = sum(v.get_ose(self).energized for v in self.vias)

        if num_energized == 2: # 1 -> 2
            # ensure other via gets power from this binding
            self._get_other_via(via).set_state(self, True)

        elif num_energized:
            # de-energize the other via (it is now the sole energy
            # provider)
            if self.num_energized: # 2 -> 1
                self._get_other_via(via).set_state(self, False)

            # energize the other via (this via is the sole energy
            # provider)
            else: # 0 -> 1
                self._get_other_via(via).set_state(self, True)

        # no vias should get power from this interconnect
        else: # 1 -> 0
            self._get_other_via(via).set_state(self, False)

        self._set_num_energized(num_energized)


Via2: TypeAlias = tuple[Via, Via]
Via4: TypeAlias = tuple[*Via2, *Via2]
Via8: TypeAlias = tuple[*Via4, *Via4]
Via16: TypeAlias = tuple[*Via8, *Via8]
Via32: TypeAlias = tuple[*Via16, *Via16]
Via64: TypeAlias = tuple[*Via32, *Via32]


class VDDStateEffector(StateEffector):
    __slots__ = (*StateEffector.__slots__, "power_rail")

    power_rail: VDD

    def __init__(self, power_rail: VDD) -> None:
        super().__init__(power_rail, self._callback)
        object.__setattr__(self, "power_rail", power_rail)

    def _callback(self, via: Via, state_changed: bool, /) -> None:
        return

    def set_state(self, energized: bool, /) -> bool:
        if not energized:
            raise ValueError("Cannot de-energize a power rail state effector")

        if not self.power_rail.energized:
            raise ValueError(
                "Attempted to energize a power rail state effector while power"
                " rail is not energized"
            )

        object.__setattr__(self, "energized", energized)
        return True


class VDD:
    def __init__(self) -> None:
        self.vias: list[Via] = list()
        self.energized: bool = False

    def register(self, *vias: Via) -> None:
        for via in vias:
            self.vias.append(via)
            via.register(VDDStateEffector(self))

    def energize(self) -> None:
        self.energized = True

        for v in self.vias:
            v.set_state(self, True)


class Interconnect:
    __slots__ = ("vias", "num_energized")

    vias: tuple[Via, ...]
    num_energized: int

    def __init__(self, *vias: Via) -> None:
        for v in vias:
            v.register(self.create_state_effector())

            if v.opposing_effectors and v.get_ose(self).energized:
                raise ValueError("Cannot interconnect an energized via")

        object.__setattr__(self, "vias", vias)
        object.__setattr__(self, "num_energized", 0)

    @classmethod
    def parallel(cls, *groups: Iterable[Via]) -> tuple[Self, ...]:
        if not groups:
            return tuple()

        groups = tuple(tuple(g) for g in groups)

        # get group length and ensure all groups are the same length
        g0, *rest = groups
        group_len = len(g0)
        for g in rest:
            if len(g) != group_len:
                raise ValueError("All groups must be of the same length")

        # create interconnects
        return tuple(cls(*vias) for vias in zip(*groups))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}[vias={self.vias!r}"
            f" num_energized={self.num_energized!r}]"
        )

    def __setattr__(self, name: str, value: Any, /) -> None:
        raise AttributeError(
            "This object does not support attribute assignment"
        )

    def register_via(self, via: Via) -> None:
        via.register(self.create_state_effector())
        object.__setattr__(self, "vias", (*self.vias, via))

    def create_state_effector(self) -> StateEffector:
        return StateEffector(self, self._handle_state_change)

    def _set_num_energized(self, num_energized: int, /) -> None:
        object.__setattr__(self, "num_energized", num_energized)

    def _handle_state_change(self, via: Via, state_changed: bool, /) -> None:
        num_energized = sum(v.get_ose(self).energized for v in self.vias)

        # all vias should get power from this interconnect
        if num_energized > 1:
            # ensure energized via that is NOT this via gets power from
            # this interconnect
            if not self.num_energized > 1: # self.num_energized==1
                for v in self.vias:
                    if v is via:
                        continue

                    if v.get_ose(self).energized:
                        v.set_state(self, True)
                        break

        # all vias except the power provider should get power from this
        # interconnect
        elif num_energized:
            # de-energize the (now) sole energy provider
            if self.num_energized > 1:
                for v in self.vias:
                    if v.get_ose(self).energized:
                        v.set_state(self, False)
                        break

            # power all vias that aren't the provider (which we know is
            # this via)
            else: # self.energized==0
                for v in self.vias:
                    if v is via:
                        continue

                    v.set_state(self, True)

        # no vias should get power from this interconnect
        else:
            for v in self.vias:
                v.set_state(self, False)

        self._set_num_energized(num_energized)


class FinFET(Cell):
    __slots__ = ("p_type", "source", "drain", "gate", "components")

    p_type: bool
    source: Via
    drain: Via
    gate: Via

    def __init__(self, p_type: bool) -> None:
        self.p_type = p_type
        self.source = Via()
        self.drain = Via()
        self.gate = Via()
        self.components = TempComponents(
            vias=[self.source, self.drain, self.gate]
        ).to_components()
        self.source.register(
            StateEffector(self, self._source_callback)
        )
        self.drain.register(
            StateEffector(self, self._drain_callback)
        )
        self.gate.register(
            StateEffector(self, self._gate_callback)
        )

    def _source_callback(self, via: Via, state_changed: bool) -> None:
        if not state_changed:
            return

        if self.gate.energized if self.p_type else not self.gate.energized:
            return

        self.drain.set_state(self, self.source.energized)

    def _gate_callback(self, via: Via, state_changed: bool) -> None:
        if not state_changed:
            return

        connected = not self.gate.energized if self.p_type else self.gate.energized

        if connected:
            self.drain.set_state(self, self.source.energized)
        else:
            self.drain.set_state(self, False)

    def _drain_callback(self, via: Via, state_changed: bool) -> None:
        return


class PTypeFinFET(FinFET):
    """A FinFET with flow when the gate is not energized."""

    def __init__(self) -> None:
        super().__init__(True)


class SignalInterface:
    def __init__(self, vias: Iterable[Via]) -> None:
        """
        :param vias: An iterable of vias where the first element is the
            first bit (LSB) and the last element is the last bit (MSB).
        :type vias: Iterable[Via]

        """

        self.vias = tuple(vias)

        for v in self.vias:
            v.register(Cap())

    def set_signal(self, signal: int, /):
        for i, v in enumerate(self.vias):
            v.set_state(Cap, not not ((signal >> i) & 1))

    def get_signal(self) -> int:
        signal: int = 0
        for i, v in enumerate(self.vias):
            signal |= v.energized << i
        return signal
