import struct as st

from thorlabs_cube.driver.message import MGMSG, Message, MsgError
from thorlabs_cube.driver.tcube.tsc import Tsc, TscSim

_RESERVED = 0x0
_CHANNEL = 0x01
_REQUEST_LENGTH = 1


class Ksc(Tsc):
    """
    KDC101 K-Cube Brushed DC Servo Motor Controller class
    """

    async def set_kcubemmi_params(
        self,
        js_mode,
        js_max_vel,
        js_accn,
        dir_sense,
        preset_pos1,
        preset_pos2,
        preset_pos3,
        disp_brightness,
        disp_timeout,
        disp_dim_level,
        js_sensitivity,
    ):
        """Set the KCube MMI (joystick) parameters.

        :param js_mode: Joystick mode (1 = velocity control, 2 = jog mode, 3 = go-to-position mode).
        :param js_max_vel: Maximum velocity for the joystick.
        :param js_accn: Acceleration for the joystick.
        :param dir_sense: Direction sense (normal or reversed).
        :param preset_pos1: Preset position 1.
        :param preset_pos2: Preset position 2.
        :param preset_pos3: Preset position 3.
        :param disp_brightness: Display brightness.
        :param disp_timeout: Display timeout in ms.
        :param disp_dim_level: Display dim level.
        :param js_sensitivity: Joystick sensitivity.
        """

        # Pack the Channel ID and all the other parameters
        payload = st.pack(
            "<HHLLLHHLLLLH",
            _CHANNEL,
            js_mode,
            js_max_vel,
            js_accn,
            dir_sense,
            preset_pos1,
            preset_pos2,
            preset_pos3,
            disp_brightness,
            disp_timeout,
            disp_dim_level,
            js_sensitivity,
        )

        # Send the message with the packed payload for MOT_SET_KCUBEMMIPARAMS (0x0520)
        await self.send(Message(MGMSG.MOT_SET_KCUBEMMIPARAMS, data=payload))

    async def get_kcubemmi_params(self):
        """Get the KCube MMI (joystick) parameters.

        :return: A tuple containing the joystick mode, max velocity,
        acceleration, direction sense, preset positions, display
        settings, and joystick sensitivity.
        """

        # Pack the Channel ID for the request payload
        payload = st.pack("<H", _CHANNEL)

        # Send the request to get the current joystick parameters
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_KCUBEMMIPARAMS, [MGMSG.MOT_GET_KCUBEMMIPARAMS], data=payload
        )

        return st.unpack("<HLLLHHLLLLH", get_msg.data[2:])

    async def set_kcubetrigio_config(
        self, trig1_mode, trig1_polarity, trig2_mode, trig2_polarity
    ):
        """Set the KCube trigger I/O configuration parameters.

        :param trig1_mode: Mode for Trigger 1 (input/output).
        :param trig1_polarity: Polarity for Trigger 1 (high/low).
        :param trig2_mode: Mode for Trigger 2 (input/output).
        :param trig2_polarity: Polarity for Trigger 2 (high/low).
        """
        # Pack the Channel ID and trigger I/O parameters
        payload = st.pack(
            "<HBBBB",
            _CHANNEL,  # Channel ID is hardcoded to 0x01
            trig1_mode,
            trig1_polarity,
            trig2_mode,
            trig2_polarity,
        )

        # Send the message with the packed payload for MOT_SET_KCUBETRIGIOCONFIG (0x0523)
        await self.send(Message(MGMSG.MOT_SET_KCUBETRIGIOCONFIG, data=payload))

    async def get_kcubetrigio_config(self):
        """Get the KCube trigger I/O configuration parameters.

        :return: A tuple containing (trig1_mode, trig1_polarity, trig2_mode, trig2_polarity).
        """
        # Pack the Channel ID for the request
        payload = st.pack("<H", _CHANNEL)  # Channel ID is hardcoded to 0x01

        # Send the request to get the current trigger I/O configuration
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_KCUBETRIGIOCONFIG,
            [MGMSG.MOT_GET_KCUBETRIGIOCONFIG],
            data=payload,
        )

        trig1_mode, trig1_polarity, trig2_mode, trig2_polarity = st.unpack(
            "<BBBB", get_msg.data[2:]
        )
        return trig1_mode, trig1_polarity, trig2_mode, trig2_polarity

    async def set_kcubepostrig_params(
        self,
        start_pos_fwd,
        interval_fwd,
        num_pulses_fwd,
        start_pos_rev,
        interval_rev,
        num_pulses_rev,
        pulse_width,
        num_cycles,
    ):
        """Set the KCube post-trigger parameters.

        :param start_pos_fwd: Stage position to start the forward trigger sequence.
        :param interval_fwd: Interval in encoder counts/microsteps for forward trigger pulses.
        :param num_pulses_fwd: Number of output pulses during forward move.
        :param start_pos_rev: Stage position to start the reverse trigger sequence.
        :param interval_rev: Interval in encoder counts/microsteps for reverse trigger pulses.
        :param num_pulses_rev: Number of output pulses during reverse move.
        :param pulse_width: Trigger output pulse width (from 1 μs to 1,000,000 μs).
        :param num_cycles: Number of forward/reverse cycles.
        """
        # Pack the Channel ID and trigger parameters
        payload = st.pack(
            "<HLLLLLLLL",
            _CHANNEL,
            start_pos_fwd,
            interval_fwd,
            num_pulses_fwd,
            start_pos_rev,
            interval_rev,
            num_pulses_rev,
            pulse_width,
            num_cycles,
        )

        await self.send(Message(MGMSG.MOT_SET_KCUBEPOSTRIGPARAMS, data=payload))

    async def get_kcubepostrig_params(self):
        """Get the KCube post-trigger parameters.

        :return: A tuple containing (start_pos_fwd, interval_fwd,
        num_pulses_fwd, start_pos_rev, interval_rev, num_pulses_rev,
        pulse_width, num_cycles).
        """

        payload = st.pack("<H", _CHANNEL)

        # Send the request to get the current post-trigger parameters
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_KCUBEPOSTRIGPARAMS,
            [MGMSG.MOT_GET_KCUBEPOSTRIGPARAMS],
            data=payload,
        )

        return st.unpack("<LLLLLLLL", get_msg.data[2:])

    class KscSim(TscSim):
        async def set_kcubemmi_params(
            self,
            js_mode: int,
            js_max_vel: int,
            js_accn: int,
            dir_sense: int,
            preset_pos1: int,
            preset_pos2: int,
            preset_pos3: int,
            disp_brightness: int,
            disp_timeout: int,
            disp_dim_level: int,
            js_sensitivity: int,
        ):
            # Store all the parameters in the simulated object
            self.js_mode = js_mode
            self.js_max_vel = js_max_vel
            self.js_accn = js_accn
            self.dir_sense = dir_sense
            self.preset_pos1 = preset_pos1
            self.preset_pos2 = preset_pos2
            self.preset_pos3 = preset_pos3
            self.disp_brightness = disp_brightness
            self.disp_timeout = disp_timeout
            self.disp_dim_level = disp_dim_level
            self.js_sensitivity = js_sensitivity

        async def get_kcubemmi_params(self):
            # Return all the stored parameters in the same order
            return (
                self.js_mode,
                self.js_max_vel,
                self.js_accn,
                self.dir_sense,
                self.preset_pos1,
                self.preset_pos2,
                self.preset_pos3,
                self.disp_brightness,
                self.disp_timeout,
                self.disp_dim_level,
                self.js_sensitivity,
            )

        async def set_kcubetrigio_config(
            self, trig1_mode, trig1_polarity, trig2_mode, trig2_polarity
        ):
            # Store trigger I/O configuration
            self.trig1_mode = trig1_mode
            self.trig1_polarity = trig1_polarity
            self.trig2_mode = trig2_mode
            self.trig2_polarity = trig2_polarity

        async def get_kcubetrigio_config(self):
            # Return the stored trigger I/O configuration
            return (
                self.trig1_mode,
                self.trig1_polarity,
                self.trig2_mode,
                self.trig2_polarity,
            )

        async def set_kcubepostrig_params(
            self,
            start_pos_fwd,
            interval_fwd,
            num_pulses_fwd,
            start_pos_rev,
            interval_rev,
            num_pulses_rev,
            pulse_width,
            num_cycles,
        ):
            # Store post-trigger parameters
            self.start_pos_fwd = start_pos_fwd
            self.interval_fwd = interval_fwd
            self.num_pulses_fwd = num_pulses_fwd
            self.start_pos_rev = start_pos_rev
            self.interval_rev = interval_rev
            self.num_pulses_rev = num_pulses_rev
            self.pulse_width = pulse_width
            self.num_cycles = num_cycles

        async def get_kcubepostrig_params(self):
            # Return the stored post-trigger parameters
            return (
                self.start_pos_fwd,
                self.interval_fwd,
                self.num_pulses_fwd,
                self.start_pos_rev,
                self.interval_rev,
                self.num_pulses_rev,
                self.pulse_width,
                self.num_cycles,
            )
