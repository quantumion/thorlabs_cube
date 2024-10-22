import asyncio
import struct as st

from thorlabs_cube.driver.base import _Cube
from thorlabs_cube.driver.message import MGMSG, Message, MsgError

_CHANNEL: int = 0x01


class Kpa(_Cube):
    """KPA101 driver implementation."""

    def __init__(self, loop: asyncio.AbstractEventLoop, serial_dev: str) -> None:
        """Initialize the KPA101 driver.

        :param loop: Event loop for asynchronous operations.
        :param serial_dev: Serial device identifier.
        """
        _Cube.__init__(self, loop, serial_dev)
        self.loop_params = None
        self.status_report_counter = 0

    async def handle_message(self, msg: Message) -> None:
        """Handle incoming messages from the KPA101 device.

        :param msg: Message object received from the device.
        """
        msg_id: MGMSG = msg.id
        data: bytes = msg.data

        if msg_id == MGMSG.HW_DISCONNECT:
            raise MsgError("Error: Please disconnect the KPA101")

        elif msg_id == MGMSG.HW_RESPONSE:
            raise MsgError("Hardware error, please disconnect and reconnect the KPA101")

        elif msg_id == MGMSG.QUAD_GET_STATUSUPDATE:
            x_diff, y_diff, sum_val, x_pos, y_pos, status_bits = st.unpack(
                "<hhIhhI", data[6:20]
            )

            # Update internal state variables with the extracted values
            self.x_diff = x_diff
            self.y_diff = y_diff
            self.sum_val = sum_val
            self.x_pos = x_pos
            self.y_pos = y_pos
            self.status_bits = status_bits

            if self.status_report_counter == 25:
                self.status_report_counter = 0
                await self.send(Message(MGMSG.QUAD_ACK_STATUSUPDATE))
            else:
                self.status_report_counter += 1

        else:
            raise MsgError(f"Unhandled message ID: {msg_id}")

    async def set_loop_params(self, p_gain: int, i_gain: int, d_gain: int) -> None:
        """Set proportional, integral, and differential feedback loop constants.

        :param p_gain: Proportional gain value.
        :param i_gain: Integral gain value.
        :param d_gain: Differential gain value.
        """
        payload = st.pack("<HHH", p_gain, i_gain, d_gain)
        await self.send(Message(MGMSG.QUAD_SET_LOOPPARAMS, data=payload))

    async def get_loop_params(self) -> tuple[int, int, int]:
        """Get proportional, integral, and differential feedback loop constants.

        :return: A tuple containing p_gain, i_gain, and d_gain values.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_LOOPPARAMS, [MGMSG.QUAD_GET_LOOPPARAMS], _CHANNEL
        )
        return st.unpack("<HHH", get_msg.data[2:])

    async def set_quad_oper_mode(self, mode: int) -> None:
        """Set the operating mode of the unit.

        :param mode: 1 for Monitor Mode, 2 for Open Loop, 3 for Closed Loop.
        """
        payload = st.pack("<H", mode)
        await self.send(Message(MGMSG.QUAD_SET_OPERMODE, data=payload))

    async def get_quad_oper_mode(self) -> int:
        """Get the operating mode of the unit.

        :return: The current operating mode of the unit.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_OPERMODE, [MGMSG.QUAD_GET_OPERMODE], _CHANNEL
        )
        return st.unpack("<H", get_msg.data[2:])[0]

    async def set_quad_position_demand_params(
        self, x_pos_min: int, x_pos_max: int, y_pos_min: int, y_pos_max: int
    ) -> None:
        """Set position demand parameters for the quad system.

        :param x_pos_min: Minimum X-axis position demand.
        :param x_pos_max: Maximum X-axis position demand.
        :param y_pos_min: Minimum Y-axis position demand.
        :param y_pos_max: Maximum Y-axis position demand.
        """
        payload = st.pack("<hhhh", x_pos_min, x_pos_max, y_pos_min, y_pos_max)
        await self.send(Message(MGMSG.QUAD_SET_POSDEMANDPARAMS, data=payload))

    async def get_quad_position_demand_params(self) -> tuple[int, int, int, int]:
        """Get position demand parameters for the quad system.

        :return: A tuple containing x_pos_min, x_pos_max, y_pos_min, and y_pos_max.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_POSDEMANDPARAMS, [MGMSG.QUAD_GET_POSDEMANDPARAMS], _CHANNEL
        )
        return st.unpack("<hhhh", get_msg.data[2:10])

    async def get_quad_status_bits(self) -> int:
        """Get the status bits of the control unit.

        :return: Status bits of the control unit.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_STATUSBITS, [MGMSG.QUAD_GET_STATUSBITS], _CHANNEL
        )
        return st.unpack("<I", get_msg.data[6:10])[0]

    async def set_quad_display_settings(
        self, disp_intensity: int, disp_mode: int, disp_dim_timeout: int
    ) -> None:
        """Set the display settings for the quad system.

        :param disp_intensity: Display intensity (0-255).
        :param disp_mode: Display mode (1 for Difference, 2 for Position).
        :param disp_dim_timeout: Dim timeout value as per documentation.
        """
        payload = st.pack("<HHH", disp_intensity, disp_mode, disp_dim_timeout)
        await self.send(Message(MGMSG.QUAD_SET_DISPSETTINGS, data=payload))

    async def get_quad_display_settings(self) -> tuple[int, int, int]:
        """Get the display settings for the quad system.

        :return: A tuple containing disp_intensity, disp_mode, and disp_dim_timeout.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_DISPSETTINGS, [MGMSG.QUAD_GET_DISPSETTINGS], _CHANNEL
        )
        return st.unpack("<HHH", get_msg.data[6:12])

    async def set_quad_position_outputs(self, x_pos: int, y_pos: int) -> None:
        """Set the X and Y position outputs.

        :param x_pos: X-axis position output value (-32768 to 32767).
        :param y_pos: Y-axis position output value (-32768 to 32767).
        """
        payload = st.pack("<hh", x_pos, y_pos)
        await self.send(Message(MGMSG.QUAD_SET_POSOUTPUTS, data=payload))

    async def get_quad_position_outputs(self) -> tuple[int, int]:
        """Get the X and Y position outputs.

        :return: A tuple containing x_pos and y_pos.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_POSOUTPUTS, [MGMSG.QUAD_GET_POSOUTPUTS], _CHANNEL
        )
        return st.unpack("<hh", get_msg.data[6:12])

    async def set_quad_loop_params2(
        self,
        p_gain: float,
        i_gain: float,
        d_gain: float,
        d_cutoff_freq: float,
        notch_freq: float,
        filter_q: float,
        notch_on: int,
        deriv_filter_on: int,
    ) -> None:
        """Set the extended loop parameters for the quad system.

        :param p_gain: Proportional gain value.
        :param i_gain: Integral gain value.
        :param d_gain: Differential gain value.
        :param d_cutoff_freq: Differential cutoff frequency.
        :param notch_freq: Notch filter frequency.
        :param filter_q: Filter quality factor.
        :param notch_on: Notch filter on/off flag.
        :param deriv_filter_on: Derivative filter on/off flag.
        """
        payload = st.pack(
            "<fffffffH",
            p_gain,
            i_gain,
            d_gain,
            d_cutoff_freq,
            notch_freq,
            filter_q,
            notch_on,
            deriv_filter_on,
        )
        await self.send(Message(MGMSG.QUAD_SET_LOOPPARAMS2, data=payload))

    async def get_quad_loop_params2(
        self,
    ) -> tuple[float, float, float, float, float, float, int, int]:
        """Get the extended loop parameters for the quad system.

        :return: A tuple containing p_gain, i_gain, d_gain, d_cutoff_freq,
        notch_freq, filter_q, notch_on, deriv_filter_on.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_LOOPPARAMS2, [MGMSG.QUAD_GET_LOOPPARAMS2], _CHANNEL
        )
        return st.unpack("<fffffffH", get_msg.data[6:36])

    async def set_trigger_config(
        self,
        trig1_mode: int,
        trig1_polarity: int,
        trig1_sum_min: int,
        trig1_sum_max: int,
        trig1_diff_threshold: int,
        trig2_mode: int,
        trig2_polarity: int,
        trig2_sum_min: int,
        trig2_sum_max: int,
        trig2_diff_threshold: int,
    ) -> None:
        """Set trigger configuration for both TRIG1 and TRIG2.

        :param trig1_mode: TRIG1 operating mode.
        :param trig1_polarity: TRIG1 polarity.
        :param trig1_sum_min: TRIG1 sum minimum.
        :param trig1_sum_max: TRIG1 sum maximum.
        :param trig1_diff_threshold: TRIG1 differential threshold.
        :param trig2_mode: TRIG2 operating mode.
        :param trig2_polarity: TRIG2 polarity.
        :param trig2_sum_min: TRIG2 sum minimum.
        :param trig2_sum_max: TRIG2 sum maximum.
        :param trig2_diff_threshold: TRIG2 differential threshold.
        """
        payload = st.pack(
            "<HHHHHHHHH",
            trig1_mode,
            trig1_polarity,
            trig1_sum_min,
            trig1_sum_max,
            trig1_diff_threshold,
            trig2_mode,
            trig2_polarity,
            trig2_sum_min,
            trig2_sum_max,
            trig2_diff_threshold,
        )
        await self.send(Message(MGMSG.QUAD_SET_TRIGGERCONFIG, data=payload))

    async def get_trigger_config(
        self,
    ) -> tuple[int, int, int, int, int, int, int, int, int, int]:
        """Get trigger configuration for both TRIG1 and TRIG2.

        :return: A tuple containing trigger configuration parameters for TRIG1 and TRIG2.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_TRIGGERCONFIG, [MGMSG.QUAD_GET_TRIGGERCONFIG], _CHANNEL
        )
        return st.unpack("<HHHHHHHHH", get_msg.data[6:24])

    async def set_digital_outputs(self, dig_ops: int) -> None:
        """Set digital outputs for TRIG1 and TRIG2.

        :param dig_ops: Status of TRIG1 and TRIG2 outputs.
        """
        payload = st.pack("<H", dig_ops)
        await self.send(Message(MGMSG.QUAD_SET_DIGOUTPUTS, data=payload))

    async def get_digital_outputs(self) -> int:
        """Get digital outputs for TRIG1 and TRIG2.

        :return: Status of TRIG1 and TRIG2 outputs.
        """
        get_msg = await self.send_request(
            MGMSG.QUAD_REQ_DIGOUTPUTS, [MGMSG.QUAD_GET_DIGOUTPUTS], _CHANNEL
        )
        return st.unpack("<H", get_msg.data[6:8])[0]

    async def set_eeprom_params(self, msg_id: int) -> None:
        """Save the parameter settings for the specified message.

        :param msg_id: The message ID of the message containing the parameters to be saved.
        """
        payload = st.pack("<H", msg_id)
        await self.send(Message(MGMSG.QUAD_SET_EEPROM_PARAMS, data=payload))


class KpaSim:
    """Simulation class for KPA101."""

    def __init__(self):

        self.loop_params = (0, 0, 0)
        self.oper_mode = 1
        self.pos_demand_params = (0, 0, 0, 0)
        self.status_bits = 0
        self.display_settings = (0, 1, 0)
        self.position_outputs = (0, 0)
        self.loop_params2 = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0)
        self.trigger_config = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.digital_outputs = 0

    def close(self):
        pass

    def set_loop_params(self, p_gain: int, i_gain: int, d_gain: int) -> None:

        self.loop_params = (p_gain, i_gain, d_gain)

    def get_loop_params(self) -> tuple[int, int, int]:
        return self.loop_params

    def set_quad_oper_mode(self, mode: int) -> None:
        self.oper_mode = mode

    def get_quad_oper_mode(self) -> int:
        return self.oper_mode

    def set_quad_position_demand_params(
        self, x_pos_min: int, x_pos_max: int, y_pos_min: int, y_pos_max: int
    ) -> None:

        self.pos_demand_params = (x_pos_min, x_pos_max, y_pos_min, y_pos_max)

    def get_quad_position_demand_params(self) -> tuple[int, int, int, int]:

        return self.pos_demand_params

    def get_quad_status_bits(self) -> int:

        return self.status_bits

    def set_quad_display_settings(
        self, disp_intensity: int, disp_mode: int, disp_dim_timeout: int
    ) -> None:

        self.display_settings = (disp_intensity, disp_mode, disp_dim_timeout)

    def get_quad_display_settings(self) -> tuple[int, int, int]:
        return self.display_settings

    def set_quad_position_outputs(self, x_pos: int, y_pos: int) -> None:

        self.position_outputs = (x_pos, y_pos)

    def get_quad_position_outputs(self) -> tuple[int, int]:
        return self.position_outputs

    def set_quad_loop_params2(
        self,
        p_gain: float,
        i_gain: float,
        d_gain: float,
        d_cutoff_freq: float,
        notch_freq: float,
        filter_q: float,
        notch_on: int,
        deriv_filter_on: int,
    ) -> None:

        self.loop_params2 = (
            p_gain,
            i_gain,
            d_gain,
            d_cutoff_freq,
            notch_freq,
            filter_q,
            notch_on,
            deriv_filter_on,
        )

    def get_quad_loop_params2(
        self,
    ) -> tuple[float, float, float, float, float, float, int, int]:
        return self.loop_params2

    def set_trigger_config(
        self,
        trig1_mode: int,
        trig1_polarity: int,
        trig1_sum_min: int,
        trig1_sum_max: int,
        trig1_diff_threshold: int,
        trig2_mode: int,
        trig2_polarity: int,
        trig2_sum_min: int,
        trig2_sum_max: int,
        trig2_diff_threshold: int,
    ) -> None:

        self.trigger_config = (
            trig1_mode,
            trig1_polarity,
            trig1_sum_min,
            trig1_sum_max,
            trig1_diff_threshold,
            trig2_mode,
            trig2_polarity,
            trig2_sum_min,
            trig2_sum_max,
            trig2_diff_threshold,
        )

    def get_trigger_config(
        self,
    ) -> tuple[int, int, int, int, int, int, int, int, int, int]:
        return self.trigger_config

    def set_digital_outputs(self, dig_ops: int) -> None:
        self.digital_outputs = dig_ops

    def get_digital_outputs(self) -> int:
        return self.digital_outputs
