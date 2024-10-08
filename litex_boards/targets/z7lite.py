#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>,
# Copyright (c) 2022 Arif Darmawan <arif.pens@gmail.com>,
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex_boards.platforms import z7lite
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.clock import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.video import VideoS7HDMIPHY
from liteeth.phy.mii import LiteEthPHYMII

# CRG ----------------------------------------------------------------------------------------------


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False,  with_video_pll=False):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_eth    = ClockDomain()
        self.clock_domains.cd_hdmi   = ClockDomain()
        self.clock_domains.cd_hdmi5x = ClockDomain()

        # # #

        # Clk
        clk50 = platform.request("clk50")

        if use_ps7_clk:
            assert sys_clk_freq == 100e6
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            # PLL.
            self.submodules.pll = pll = S7PLL(speedgrade=-2)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk50, 50e6)
            pll.create_clkout(self.cd_sys,    sys_clk_freq)
            pll.create_clkout(self.cd_eth,    25e6)
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)  # Ignore sys_clk to pll.clkin

        # Video PLL.
        if with_video_pll:
            self.submodules.video_pll = video_pll = S7MMCM(speedgrade=-2)
            video_pll.reset.eq(self.rst)
            video_pll.register_clkin(clk50, 50e6)
            video_pll.create_clkout(self.cd_hdmi,   40e6)
            video_pll.create_clkout(self.cd_hdmi5x, 5*40e6)

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_led_chaser=True, with_ethernet=False,
                 with_etherbone=False, with_video_terminal=False, **kwargs):
        platform = z7lite.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq, with_video_pll=with_video_terminal)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Z7lite", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            raise NotImplementedError

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads=self.platform.request("eth_clocks"),
                pads=self.platform.request("eth")
            )
            platform.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets eth_clocks_tx_IBUF]")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal:
            self.submodules.videophy = VideoS7HDMIPHY(platform.request("hdmi_out"), clock_domain="hdmi")
            self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="hdmi")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads=platform.request_all("user_led"),
                sys_clk_freq=sys_clk_freq)

# Build --------------------------------------------------------------------------------------------


def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on Z7lite")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",                action="store_true", help="Build design.")
    target_group.add_argument("--load",                 action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",         default=100e6,       help="System clock frequency.")
    target_group.add_argument("--with-video-terminal",  action="store_true", help="Enable Video Terminal (HDMI).")
    target_group.add_argument("--with-ethernet",        action="store_true", help="Enable Ethernet support.")
    target_group.add_argument("--with-etherbone",       action="store_true", help="Enable Etherbone support.")
    builder_args(parser)
    soc_core_args(parser)
    vivado_build_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_ethernet       = args.with_ethernet,
        with_etherbone      = args.with_etherbone,
        with_video_terminal = args.with_video_terminal,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build(**vivado_build_argdict(args))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(
            builder.get_bitstream_filename(mode="sram"), device=1)


if __name__ == "__main__":
    main()
