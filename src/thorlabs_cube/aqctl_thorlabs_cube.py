#!/usr/bin/env python3
"""NDSP entrypoint script that initializes the device and start the control server"""

import argparse
import asyncio

from sipyco import common_args
from sipyco.pc_rpc import simple_server_loop

from thorlabs_cube.driver.kcube.kdc import Kdc, KdcSim
from thorlabs_cube.driver.tcube.tdc import Tdc, TdcSim
from thorlabs_cube.driver.tcube.tpz import Tpz, TpzSim


def get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-P",
        "--product",
        required=True,
        help="type of the Thorlabs T/K-Cube device to control: tdc001/tpz00/kdc101",
    )
    parser.add_argument(
        "-d",
        "--device",
        default=None,
        help="serial device. See documentation for how to specify a USB Serial"
        " Number.",
    )
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Put the driver in simulation mode, even if --device is used.",
    )
    common_args.simple_network_args(parser, 3255)
    common_args.verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    common_args.init_logger_from_args(args)

    if not args.simulation and args.device is None:
        raise ValueError(
            "You need to specify either --simulation or -d/--device argument. "
            "Use --help for more information."
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        product = args.product.lower()
        if args.simulation:
            if product == "tdc001":
                dev = TdcSim()
            elif product == "tpz001":
                dev = TpzSim()
            elif product == "kdc101":
                dev = KdcSim()
            else:
                raise ValueError(
                    "Invalid product string (-P/--product). Choose from tdc001, tpz001, or kdc101"
                )
        else:
            if product == "tdc001":
                dev = Tdc(args.device)
            elif product == "tpz001":
                dev = Tpz(args.device)
                loop.run_until_complete(dev.get_tpz_io_settings())
            elif product == "kdc101":
                dev = Kdc(args.device)
            else:
                raise ValueError(
                    "Invalid product string (-P/--product). Choose from tdc001, tpz001, or kdc101"
                )

        try:
            simple_server_loop(
                {product: dev},
                common_args.bind_address_from_args(args),
                args.port,
                loop=loop,
            )
        finally:
            dev.close()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
