#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2022 Arif Darmawan <arif.pens@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk50", 0, Pins("N18"), IOStandard("LVCMOS33")),

    ("user_btn", 0, Pins("P16"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("T12"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("P15"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("U12"), IOStandard("LVCMOS33")),

    # HDMI
    ("hdmi_out", 0,
        Subsignal("clk_p",   Pins("U18"), IOStandard("TMDS_33")),
        Subsignal("clk_n",   Pins("U19"), IOStandard("TMDS_33")),
        Subsignal("data0_p", Pins("V20"), IOStandard("TMDS_33")),
        Subsignal("data0_n", Pins("W20"), IOStandard("TMDS_33")),
        Subsignal("data1_p", Pins("T20"), IOStandard("TMDS_33")),
        Subsignal("data1_n", Pins("U20"), IOStandard("TMDS_33")),
        Subsignal("data2_p", Pins("N20"), IOStandard("TMDS_33")),
        Subsignal("data2_n", Pins("P20"), IOStandard("TMDS_33")),
        Subsignal("scl",     Pins("R19"), IOStandard("LVCMOS33")),
        Subsignal("sda",     Pins("T19"), IOStandard("LVCMOS33")),
        Subsignal("hdp",     Pins("P19"), IOStandard("LVCMOS33")),
    ),

    # MII Ethernet
    ("eth_clocks", 0,
        Subsignal("tx", Pins("L14")),
        Subsignal("rx", Pins("K17")),
        IOStandard("LVCMOS33"),
     ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("H20")),
        Subsignal("mdio",    Pins("J15"), Misc("SLEW=FAST")),
        Subsignal("mdc",     Pins("G14"), Misc("SLEW=FAST")),
        Subsignal("rx_dv",   Pins("K18")),
        #Subsignal("rx_er",   Pins()),
        Subsignal("rx_data", Pins("J14 K14 M18 M17")),
        Subsignal("tx_en",   Pins("N16"), Misc("SLEW=FAST")),
        Subsignal("tx_data", Pins("M14 L15 M15 N15"), Misc("SLEW=FAST")),
        #Subsignal("col",     Pins("")),
        #Subsignal("crs",     Pins("")),
        IOStandard("LVCMOS33")
     ),

    # LAN8720 RMII Ethernet
    # USE External GPIO2 with modified Waveshare Module
    ("lan8720_eth_clocks", 0,
        Subsignal("ref_clk", Pins("F19")),
        IOStandard("LVCMOS33"),
    ),
    ("lan8720_eth", 0,
        Subsignal("rx_data", Pins("M19 M20")),
        Subsignal("crs_dv",  Pins("F20")),
        Subsignal("tx_en",   Pins("K19")),
        Subsignal("tx_data", Pins("J19 J20")),
        IOStandard("LVCMOS33")
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("L16")),
        Subsignal("rx", Pins("L17")),
        IOStandard("LVCMOS33")
    ),
]

_ps7_io = [
    # PS7
    ("ps7_clk",   0, Pins(1)),
    ("ps7_porb",  0, Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio",   0, Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ba",      Pins(3)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("dm",      Pins(4)),
        Subsignal("dq",      Pins(32)),
        Subsignal("dqs_n",   Pins(4)),
        Subsignal("dqs_p",   Pins(4)),
        Subsignal("odt",     Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("vrn",     Pins(1)),
        Subsignal("vrp",     Pins(1)),
     ),
]

# Connectors ---------------------------------------------------------------------------------------
# GPIO1 & GPIO2 start from pad 1 (square soldering pad)
_connectors = [
    ("gpio1",
        "N17 P18",
        "R16 R17",
        "T16 U17",
        "W18 W19",
        "Y18 Y19",
        # 5V  GND
        "Y16 Y17",
        "V17 V18",
        "W14 Y14",
        "V16 W16",
        "T17 R18",
        "V12 W13",
        "T14 T15",
        "T11 T10",
        # 3V3 GND
        "V15 W15",
        "P14 R14",
        "U14 U15",
        "U13 V13",
        "T12 U12"),
    ("gpio2",
        "L16 L17",
        "H15 G15",
        "F16 F17",
        "E18 E19",
        "B19 A20",
        # 5V  GND
        "D19 D20",
        "E17 D18",
        "H16 H17",
        "G19 G20",
        "J18 H18",
        "K16 J16",
        "C20 B20",
        "G17 G18",
        # 3V3 GND
        "L19 L20",
        "F19 F20",
        "M19 M20",
        "K19 J19",
        "J20 H20"),
]

# Platform -----------------------------------------------------------------------------------------


class Platform(XilinxPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="vivado"):
        XilinxPlatform.__init__(self, "xc7z020-clg400-2",
                                _io,  _connectors, toolchain=toolchain)
        self.add_extension(_ps7_io)
        # self.add_extension(_usb_uart_pmod_io)

    def create_programmer(self):
        return VivadoProgrammer()

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(
            self.lookup_request("clk50", loose=True), 1e9/50e6)
