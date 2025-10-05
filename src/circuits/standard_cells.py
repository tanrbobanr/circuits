from __future__ import annotations
from typing import Generator

from .core import (
    PTypeFinFET,
    VDD,
    Via,
    Interconnect,
    Via16,
    Via2,
    Binding,
    Cell,
    TempComponents,
)


class NOT(Cell):
    __slots__ = ("i", "o")

    i: Via
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET()
        cmp.add(p0)

        # rails
        vdd.register(p0.source)

        # expose vias
        self.i = p0.gate
        self.o = p0.drain
        self.components = cmp.to_components()


class NOR2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET()
        p1 = PTypeFinFET()
        cmp.add(p0, p1)

        # rails
        vdd.register(p0.source)

        # interconnects and bindings
        cmp.add(Binding(p0.drain, p1.source))

        # expose vias
        self.i = (p0.gate, p1.gate)
        self.o = p1.drain
        self.components = cmp.to_components()


class OR2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET()
        p1 = PTypeFinFET()
        p2 = PTypeFinFET()
        cmp.add(p0, p1, p2)

        # rails
        vdd.register(p0.source, p2.source)

        # interconnects and bindings
        cmp.add(
            Binding(p0.drain, p1.source),
            Binding(p1.drain, p2.gate),
        )

        # expose vias
        self.i = (p0.gate, p1.gate)
        self.o = p2.drain
        self.components = cmp.to_components()


class OR3(Cell):
    __slots__ = ("i", "o")

    i: tuple[Via, Via, Via]
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        or2_0 = OR2(vdd)
        or2_1 = OR2(vdd)
        cmp.add(or2_0, or2_1)

        cmp.add(Binding(or2_1.i[0], or2_0.o))

        self.i = (*or2_0.i, or2_1.i[1])
        self.o = or2_1.o
        self.components = cmp.to_components()


class NAND2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET()
        p1 = PTypeFinFET()
        cmp.add(p0, p1)

        # rails
        vdd.register(p0.source, p1.source)

        # vias
        o = Via()
        cmp.add(o)

        # interconnects and bindings
        cmp.add(Interconnect(p0.drain, p1.drain, o))

        # expose vias
        self.i = (p0.gate, p1.gate)
        self.o = o
        self.components = cmp.to_components()


class AND2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET()
        p1 = PTypeFinFET()
        p2 = PTypeFinFET()
        cmp.add(p0, p1, p2)

        # rails
        vdd.register(p0.source, p1.source, p2.source)

        # interconnects and bindings
        cmp.add(Interconnect(p0.drain, p1.drain, p2.gate))

        # expose vias
        self.i = (p0.gate, p1.gate)
        self.o = p2.drain
        self.components = cmp.to_components()


class XOR2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET() # i0a
        p1 = PTypeFinFET() # i1a
        p2 = PTypeFinFET() # i0b
        p3 = PTypeFinFET() # i1b
        p4 = PTypeFinFET() # o
        cmp.add(p0, p1, p2, p3, p4)

        # rails
        vdd.register(p0.source, p2.source, p3.source)

        # vias
        i0 = Via()
        i1 = Via()
        cmp.add(i0, i1)

        # interconnects and bindings
        cmp.add(
            Binding(p0.drain, p1.source),
            Binding(p1.drain, p4.gate),
            Interconnect(i0, p0.gate, p2.gate),
            Interconnect(i1, p1.gate, p3.gate),
            Interconnect(p2.drain, p3.drain, p4.source)
        )

        # expose vias
        self.i = (i0, i1)
        self.o = p4.drain
        self.components = cmp.to_components()


class XNOR2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # transistors
        p0 = PTypeFinFET() # i0a
        p1 = PTypeFinFET() # i1a
        p2 = PTypeFinFET() # i0b
        p3 = PTypeFinFET() # i1b
        p4 = PTypeFinFET() # gate
        cmp.add(p0, p1, p2, p3, p4)

        # rails
        vdd.register(p0.source, p1.source, p2.source, p4.source)

        # vias
        i0 = Via()
        i1 = Via()
        o = Via()
        cmp.add(i0, i1, o)

        # interconnects and bindings
        cmp.add(
            Binding(p2.drain, p3.source),
            Interconnect(p0.drain, p1.drain, p4.gate),
            Interconnect(o, p4.drain, p3.drain),
            Interconnect(i0, p0.gate, p2.gate),
            Interconnect(i1, p1.gate, p3.gate)
        )

        # expose vias
        self.i = (i0, i1)
        self.o = o
        self.components = cmp.to_components()


class BUF1(Cell):
    __slots__ = ("i", "o")

    i: Via
    o: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        self.i = self.o = Via()
        cmp.add(self.i)
        self.components = cmp.to_components()


class BUF2(Cell):
    __slots__ = ("i", "o")

    i: Via2
    o: Via2

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        self.i = self.o = (Via(), Via())
        cmp.add(*self.i)
        self.components = cmp.to_components()


class HalfAdder(Cell):
    __slots__ = ("i", "s", "c")

    i: Via2
    s: Via
    c: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # cells
        x = XOR2(vdd)
        a = AND2(vdd)
        cmp.add(x, a)

        # vias
        i0 = Via()
        i1 = Via()
        cmp.add(i0, i1)

        # interconnects and bindings
        cmp.add(
            Interconnect(i0, x.i[0], a.i[0]),
            Interconnect(i1, x.i[1], a.i[1])
        )

        # expose vias
        self.i = (i0, i1)
        self.s = x.o
        self.c = a.o
        self.components = cmp.to_components()


class FullAdder(Cell):
    __slots__ = ("i", "cin", "s", "cout")

    i: tuple[Via, Via]
    cin: Via
    s: Via
    cout: Via

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # cells
        h0 = HalfAdder(vdd)
        h1 = HalfAdder(vdd)
        or2 = OR2(vdd)
        cmp.add(h0, h1, or2)

        # interconnects and bindings
        cmp.add(
            Binding(h0.s, h1.i[0]),
            Binding(h0.c, or2.i[0]),
            Binding(h1.c, or2.i[1])
        )

        # expose vias
        self.i = h0.i
        self.cin = h1.i[1]
        self.s = h1.s
        self.cout = or2.o
        self.components = cmp.to_components()


class PG(Cell):
    __slots__ = ("i", "o")

    i: Via2
    """The two input signals ``(A[i:i], B[i:i])``"""

    o: Via2
    """The output PG signals ``(P[i:i], G[i:i])``"""

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # cells
        and2 = AND2(vdd)
        xor2 = XOR2(vdd)
        cmp.add(and2, xor2)

        # vias
        i0 = Via()
        i1 = Via()
        cmp.add(i0, i1)

        # bindings and interconnects
        cmp.add(
            Interconnect(i0, and2.i[0], xor2.i[0]),
            Interconnect(i1, and2.i[1], xor2.i[1])
        )

        # expose vias
        self.i = (i0, i1)
        self.o = (xor2.o, and2.o)
        self.components = cmp.to_components()


class PGCin(Cell):
    __slots__ = ("i", "cin", "o")

    i: Via2
    """The two input signals ``(A[i:i], B[i:i])``"""

    cin: Via

    o: Via2
    """The output PG signals ``(P[i:i], G[i:i])``"""

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # cells
        and2_ga = AND2(vdd)
        and2_gb = AND2(vdd)
        and2_gc = AND2(vdd)
        or3 = OR3(vdd)
        xor2 = XOR2(vdd)
        cmp.add(and2_ga, and2_gb, and2_gc, or3, xor2)

        # vias
        i0 = Via()
        i1 = Via()
        cin = Via()
        cmp.add(i0, i1, cin)

        # bindings and interconnects
        cmp.add(
            Interconnect(i0, and2_ga.i[0], and2_gc.i[0], xor2.i[0]),
            Interconnect(i1, and2_gb.i[0], and2_gc.i[1], xor2.i[1]),
            Interconnect(cin, and2_ga.i[1], and2_gb.i[1]),
            Binding.parallel(or3.i, (and2_ga.o, and2_gb.o, and2_gc.o))
        )

        # expose vias
        self.i = (i0, i1)
        self.cin = cin
        self.o = (xor2.o, or3.o)
        self.components = cmp.to_components()


class PGMergeR2(Cell):
    __slots__ = ("i0", "i1", "o")

    i0: Via2
    """The PG pair ``(p[i:k], g[i:k])``"""

    i1: Via2
    """The PG pair ``(p[k-1:j], g[k-1:j])``"""

    o: tuple[Via, Via]
    """The output PG pair ``(p[i:j],g[i:j])``"""

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # cells
        and2_0 = AND2(vdd)
        and2_1 = AND2(vdd)
        or2 = OR2(vdd)
        cmp.add(and2_0, and2_1, or2)

        # vias
        p_ik = Via()
        cmp.add(p_ik)

        # interconnects and bindings
        cmp.add(
            Binding(and2_1.o, or2.i[0]),
            Interconnect(p_ik, and2_0.i[1], and2_1.i[1])
        )

        # expose vias
        self.i0 = (p_ik, or2.i[1])
        self.i1 = (and2_0.i[0], and2_1.i[0])
        self.o = (and2_0.o, or2.o)
        self.components = cmp.to_components()


class PGHalfMergeR2(Cell):
    __slots__ = ("i0", "i1", "o")

    i0: Via2
    """The PG pair ``(p[i:k], g[i:k])``"""

    i1: Via
    """The generate bit ``g[k-1:j]``"""

    o: Via
    """The output generate ``g[i:j]``"""

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()

        # cells
        and2 = AND2(vdd)
        or2 = OR2(vdd)
        cmp.add(and2, or2)

        # interconnects and bindings
        cmp.add(Binding(and2.o, or2.i[0]))

        # expose vias
        self.i0 = (and2.i[1], or2.i[1])
        self.i1 = and2.i[0]
        self.o = or2.o
        self.components = cmp.to_components()
