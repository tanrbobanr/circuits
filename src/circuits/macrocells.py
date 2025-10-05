from typing import Generator, ClassVar

from .core import Cell, Via, Via16, Via32, Via64, Interconnect, TempComponents, VDD, Binding
from .standard_cells import PG, PGCin, PGMergeR2, PGHalfMergeR2, BUF1, XOR2


class _KSAR2Cin(Cell):
    __slots__ = ("i0", "i1", "cin", "o", "cout", "layers")

    i0: tuple[Via, ...]
    i1: tuple[Via, ...]
    cin: Via
    o: tuple[Via, ...]
    cout: Via
    layers: tuple[tuple[Cell, ...]]
    height: ClassVar[int]

    def _init(self, vdd: VDD) -> None:
        cmp = TempComponents()
        layers: list[Cell] = list()
        width = 2 ** self.height

        # GENERATE
        pgs = (PGCin(vdd), *tuple(PG(vdd) for _ in range(width - 1)))
        cmp.add(*pgs)
        layers.append(pgs)
        p_orig = (pgs[0].o[0], *tuple(Via() for _ in range(width - 1)))
        cmp.add(*p_orig[1:])
        pgos = tuple((Via(), pg.o[1]) for pg in pgs[1:])
        cmp.add(*tuple(pgo[0] for pgo in pgos))
        gos = (pgs[0].o[1],)
        cmp.add(*Interconnect.parallel(
            p_orig[1:],
            (pg.o[0] for pg in pgs[1:]),
            (pgo[0] for pgo in pgos)
        ))

        # GROUP PG
        for layer in range(self.height):
            half_offset: int = 2 ** layer
            offset = half_offset * 2
            full_count = width - offset

            # build layer components
            l_full = tuple(PGMergeR2(vdd) for _ in range(full_count))
            l_half = tuple(PGHalfMergeR2(vdd) for _ in range(half_offset))
            l_buf = tuple(BUF1(vdd) for _ in range(half_offset))
            cmp.add(*(l_full + l_half + l_buf))

            layers.append((*l_buf, *l_half, *l_full))

            # l_full connections
            for i, cell in enumerate(l_full):
                cell2_index = i + half_offset

                if cell2_index < full_count:
                    cell2 = l_full[cell2_index]
                    cmp.add(*Interconnect.parallel(
                        pgos[i + half_offset], cell.i0, cell2.i1
                    ))
                else:
                    cmp.add(Binding.parallel(pgos[i + half_offset], cell.i0))

            # l_half connections
            if layer != (self.height - 1): # is not last layer
                for i, cell in enumerate(l_half):
                    cmp.add(*Interconnect.parallel(
                        pgos[i], cell.i0, l_full[i].i1
                    ))
            else:
                for i, cell in enumerate(l_half):
                    cmp.add(*Interconnect.parallel(pgos[i], cell.i0))

            # l_buf connections
            for i, cell in enumerate(l_buf):
                cmp.add(Interconnect(gos[i], cell.i, l_half[i].i1))

            # build new pgos and gos
            pgos = tuple(cell.o for cell in l_full)
            gos = tuple(cell.o for cell in l_buf + l_half)

        # SUMS AND COUT
        cin = Via()
        sum_xors = tuple(XOR2(vdd) for _ in range(width))
        cmp.add(cin, *sum_xors)
        layers.append(sum_xors)

        # connect xor inputs
        for i, xor in enumerate(sum_xors):
            cmp.add(Binding(xor.i[0], p_orig[i]))
            if i:
                cmp.add(Binding(xor.i[1], gos[i - 1]))
            else:
                cmp.add(Interconnect(xor.i[1], cin, pgs[0].cin))

        sums = tuple(x.o for x in sum_xors)
        cout = gos[-1]

        # BINDINGS
        self.i0 = tuple(pg.i[0] for pg in pgs)
        self.i1 = tuple(pg.i[1] for pg in pgs)
        self.cin = cin
        self.o = sums
        self.cout = cout
        self.layers = layers
        self.components = cmp.to_components()

    def _diagram(self) -> Generator[str, None, None]:
        yield " ".join(
            str(i).ljust(2) for i in range((2 ** self.height) - 1, -1, -1)
        )

        type_map = {
            PG: "G ",
            PGCin: "< ",
            PGMergeR2: "X ",
            PGHalfMergeR2: "Y ",
            BUF1: "| ",
            XOR2: "S ",
        }

        for l in self.layers:
            yield " ".join(type_map[type(c)] for c in reversed(l))

    def diagram(self) -> str:
        return "\n".join(self._diagram())

    def _state_diagram(self) -> Generator[str, None, None]:
        yield " ".join(
            str(i).ljust(3) for i in range(2 ** self.height, -2, -1)
        )

        c_grey = "\033[90m"
        c_red = "\033[31m"
        c_blue = "\033[34m"
        c_green = "\033[32m"
        c_cyan = "\033[96m"
        c_clr = "\033[0m"

        type_map = {
            PG: f"{c_grey}G",
            PGCin: f"{c_grey}<",
            PGMergeR2: f"{c_grey}X",
            PGHalfMergeR2: f"{c_grey}Y",
            BUF1: f"{c_grey}|",
            XOR2: f"{c_grey}S",
        }
        dual_out = (PG, PGCin, PGMergeR2)
        single_out = (PGHalfMergeR2, BUF1, XOR2)

        def ie(via: Via) -> int:
            return int(via.energized)

        def convert(value: Cell) -> str:
            tp = type(value)
            p = type_map[tp]

            if isinstance(value, dual_out):
                return f"{p}{c_red}{ie(value.o[0])}{c_blue}{ie(value.o[1])}"
            elif isinstance(value, single_out):
                return f"{p}{c_green}{ie(value.o)} "
            else:
                return "???"

        last_layer = len(self.layers) - 1

        for i, l in enumerate(self.layers):
            l_str = " ".join(convert(c) for c in reversed(l))
            if not i:
                yield f"    {l_str} {c_grey}Ci{c_cyan}{ie(self.cin)}{c_clr}"
            elif i == last_layer:
                yield f"{c_grey}Co{c_cyan}{ie(self.cout)} {l_str}{c_clr}"
            else:
                yield f"    {l_str}{c_clr}"

    def state_diagram(self) -> str:
        return "\n".join(self._state_diagram())


class KSA16R2Cin(_KSAR2Cin):
    height = 4
    i0: Via16
    i1: Via16
    o: Via16


class KSA32R2Cin(_KSAR2Cin):
    height = 5
    i0: Via32
    i1: Via32
    o: Via32


class KSA64R2Cin(_KSAR2Cin):
    height = 6
    i0: Via64
    i1: Via64
    o: Via64
