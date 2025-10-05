from src.circuits import *


def main() -> None:
    vdd = VDD()

    ksa = KSA64R2Cin(vdd)

    ksa.cin.register(Cap())
    ksa.cout.register(Cap())

    i0_int = SignalInterface(ksa.i0)
    i1_int = SignalInterface(ksa.i1)
    o_int = SignalInterface(ksa.o)

    vdd.energize()

    i_min = 0
    i_max = (1 << 64) - 1

    while True:
        try:
            # get user input
            i0 = int(input("Input A: "))
            if not (i_min <= i0 <= i_max):
                print(
                    f"Input out of range (must be <= {i_min} and >= {i_max})"
                )
                continue

            i1 = int(input("Input B: "))
            if not (i_min <= i1 <= i_max):
                print(
                    f"Input out of range (must be <= {i_min} and >= {i_max})"
                )
                continue

            cin = ({"t": True, "f": False}).get(
                input("Carry-in (T/f): ").lower()
            )
            if cin is None:
                print("Input must be either 't' or 'f' (case-insensitive)")
                continue

            # set inputs
            i0_int.set_signal(i0)
            i1_int.set_signal(i1)
            ksa.cin.set_state(Cap, cin)

            # show output
            print(f">>> {o_int.get_signal()} cout={int(ksa.cout.energized)}")

        except KeyboardInterrupt:
            print()
            return


if __name__ == "__main__":
    main()
