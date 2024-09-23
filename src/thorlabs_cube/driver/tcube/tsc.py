import struct as st

from thorlabs_cube.driver.base import _Cube
from thorlabs_cube.driver.message import MGMSG, Message, MsgError

_CHANNEL = 0x01
_RESERVED = 0x00


class Tsc(_Cube):
    """TSC001 T-Cube Motor Controller class"""

    def __init__(self, *args, **kwargs):
        _Cube.__init__(self, *args, **kwargs)
        self.status_report_counter = 0

    async def handle_message(self, msg):
        msg_id = msg.id
        data = msg.data

        if msg_id == MGMSG.HW_DISCONNECT:
            raise MsgError("Error: Please disconnect the TDC001")
        elif msg_id == MGMSG.HW_RESPONSE:
            raise MsgError(
                "Hardware error, please disconnect " "and reconnect the TDC001"
            )
        elif msg_id == MGMSG.HW_RICHRESPONSE:
            (code,) = st.unpack("<H", data[2:4])
            raise MsgError(
                "Hardware error {}: {}".format(code, data[4:].decode(encoding="ascii"))
            )
        elif (
            msg_id == MGMSG.MOT_MOVE_COMPLETED
            or msg_id == MGMSG.MOT_MOVE_STOP
            or msg_id == MGMSG.MOT_GET_STATUSUPDATE
        ):
            if self.status_report_counter == 25:
                self.status_report_counter = 0
                await self.send(Message(MGMSG.MOT_MOVE_COMPLETED))
            else:
                self.status_report_counter += 1
            (
                self.position,
                self.encoder_count,
                self.status_bits,
                self.chan_identity_two,
                _RESERVED,
                _RESERVED,
                _RESERVED,
            ) = st.unpack(
                "<LLLHLLL",
                data[2:],
            )

    def module_identify(self):
        return super().module_identify()

    def hardware_start_update_messages(self, update_rate):
        return super().hardware_start_update_messages(update_rate)

    def hardware_stop_update_messages(self):
        return super().hardware_stop_update_messages()

    def hardware_request_information(self):
        return (
            super().hardware_request_information()
        )  # FIXME->need to change serialization format but should work after that

    def is_channel_enabled(self):
        return super().is_channel_enabled()

    def ping(self):
        return super().ping()

    async def set_channel_enable_state(self, activated):
        return await super().set_channel_enable_state(activated)

    async def get_channel_enable_state(self):
        return await super().get_channel_enable_state()

    # functions from base class definition end

    async def get_bay_used(self):
        """Identify which bay is being used by the controller on Thorlabs Hub

        :param absolute_position: The absolute position in encoder counts.
                                E.g., 200,000 counts for 10 mm.
        """
        get_msg = await self.send_request(
            MGMSG.HUB_REQ_BAYUSED, [MGMSG.HUB_GET_BAYUSED], 1
        )

        used_bay_ident = get_msg.param1
        return used_bay_ident

    async def set_absolute_position(self, absolute_position):
        """Move the motor to an absolute position.

        :param absolute_position: The absolute position in encoder counts.
                                E.g., 200,000 counts for 10 mm.
        """

        # Pack the Channel ID (2 bytes) and the Absolute Position (4 bytes)
        payload = st.pack("<Hl", 1, absolute_position)

        await self.send_request(
            MGMSG.MOT_MOVE_ABSOLUTE,
            [MGMSG.MOT_MOVE_COMPLETED, MGMSG.MOT_MOVE_STOPPED],
            data=payload,
        )

    async def move_stop(self, stop_mode):
        """Stop any type of motor move (relative, absolute, homing, or velocity).

        :param stop_mode: The stop mode (1 for immediate stop, 2 for profiled stop).
        """

        # Send the message with the command ID (0x0465), and put channel ID in param1 and stop mode in param2
        await self.send_request(
            "<BB",
            MGMSG.MOT_MOVE_STOP,
            [MGMSG.MOT_MOVE_STOPPED],
            param1=_CHANNEL,
            param2=stop_mode,
        )

    async def set_av_modes(self, mode_bits):
        """Set the LED indicator modes based on the provided mode_bits.

        :param mode_bits: A bitmask indicating which modes to enable:
                        - 1 (LEDMODE_IDENT): LED flashes when 'Ident' is sent.
                        - 2 (LEDMODE_LIMITSWITCH): LED flashes when motor reaches limit switch.
                        - 8 (LEDMODE_MOVING): LED is lit when the motor is moving.
        """

        # Pack the Channel ID (2 bytes) and ModeBits (4 bytes)
        payload = st.pack("<Hl", 1, mode_bits)

        # Send the message with the packed payload for MOT_SET_AVMODES (0x04B3)
        await self.send(Message(MGMSG.MOT_SET_AVMODES, data=payload))

    async def get_av_modes(self):
        """Get the current LED indicator mode bits.

        :return: The LED mode bits.
        """

        # Send the request to get the current AV modes for the specified channel
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_AVMODES, [MGMSG.MOT_GET_AVMODES], 1
        )

        mode_bits = get_msg.data[2:]
        return mode_bits

    async def set_button_parameters(
        self, mode, position1, position2, timeout1, timeout2
    ):
        """Set button parameters for the front panel buttons.

        :param mode: Mode for the buttons (1 for jog, 2 for position mode).
        :param position1: Position in encoder counts for the top button.
        :param position2: Position in encoder counts for the bottom button.
        :param timeout1: Timeout in ms for position1.
        :param timeout2: Timeout in ms for position2.
        """

        # Pack the channel ID, mode, position1, position2, timeout1, and timeout2
        payload = st.pack("<HHllHH", 1, mode, position1, position2, timeout1, timeout2)

        # Send the message with the packed payload for MOT_SET_BUTTONPARAMS (0x04B6)
        await self.send(Message(MGMSG.MOT_SET_BUTTONPARAMS, data=payload))

    async def get_button_parameters(self):
        """Get the current button parameters.

        :return: A tuple containing (mode, position1, position2, timeout1, timeout2)
        """

        # Send the request for button parameters (MOT_REQ_BUTTONPARAMS 0x04B7)
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_BUTTONPARAMS, [MGMSG.MOT_GET_BUTTONPARAMS], 1
        )

        mode, position1, position2, timeout1, timeout2 = st.unpack(
            "<HllHH", get_msg.data[2:]
        )

        return mode, position1, position2, timeout1, timeout2

    async def set_eeprom_parameters(self, msg_id):
        """Save the current parameters for the specified message in the EEPROM.

        This function sends a request to the device to save the parameter settings
        of the specified message to the EEPROM memory, ensuring the settings are
        retained even after the device is powered off.

        :param msg_id: The message ID of the message containing the parameters
                       that need to be saved in the EEPROM.
        """

        payload = st.pack("<HH", 1, msg_id)

        await self.send(Message(MGMSG.MOT_SET_EEPROMPARAMS, data=payload))

    async def get_status_update(self):
        """Returns a status update on the specified motor channel

        This function sends a request to the device to return status updates of
        position, encoder count, status bits on channel one as well as, for future use,
        returns channel identity two and its associated data which is garbage right now

        """

        get_msg = await self.send_request(
            MGMSG.MOT_REQ_STATUSUPDATE, [MGMSG.MOT_GET_STATUSUPDATE], _CHANNEL
        )

        (
            position,
            encoder_count,
            status_bits,
            chan_identity_two,
            _RESERVED,
            _RESERVED,
            _RESERVED,
        ) = st.unpack("<HIIIHIII", get_msg.data[2:])

        return position, encoder_count, status_bits, chan_identity_two

        # need to test this on the container with devices connected

    async def set_sol_operating_mode(self, operating_mode):
        """Set the solenoid operating mode for the single channel.

        :param operating_mode: The operating mode to set (e.g., 1, 2, etc.).
        """

        # Send the message with the packed payload
        await self.send(Message(MGMSG.MOT_SET_SOL_OPERATINGMODE, param2=operating_mode))

    async def get_sol_operating_mode(self):
        """Get the current solenoid operating mode for the single channel."""
        # Send the request to get the solenoid operating mode for channel 1
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_SOL_OPERATINGMODE,
            [MGMSG.MOT_GET_SOL_OPERATINGMODE],
            param1=1,  # Fixed channel ID
        )
        # The returned mode is in param2
        return get_msg.param2

    async def set_solenoid_cycle_parameters(self, on_time, off_time, num_cycles):
        """Set the solenoid cycle parameters.

        :param on_time: Time (in ms) the solenoid stays on (100ms to 10,000ms).
        :param off_time: Time (in ms) the solenoid stays off (100ms to 10,000ms).
        :param num_cycles: Number of open/close cycles (0 for infinite, up to 1,000,000).
        """

        # Pack the Channel ID, OnTime, OffTime, and NumCycles
        payload = st.pack("<HLLL", 1, on_time, off_time, num_cycles)

        # Send the message with the packed payload for MOT_SET_SOL_CYCLEPARAMS (0x04C3)
        await self.send(Message(MGMSG.MOT_SET_SOL_CYCLEPARAMS, data=payload))

    async def get_solenoid_cycle_parameters(self):
        """Get the current solenoid cycle parameters.

        :return: A tuple containing (on_time, off_time, num_cycles).
        """

        # Pack the Channel ID for the request
        payload = st.pack("<H", 1)

        # Send the request to get the current solenoid cycle parameters
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_SOL_CYCLEPARAMS, [MGMSG.MOT_GET_SOL_CYCLEPARAMS], data=payload
        )

        on_time, off_time, num_cycles = st.unpack("<LLL", get_msg.data[2:])

        return on_time, off_time, num_cycles

    async def set_sol_interlock_mode(self, mode):
        """Set the solenoid interlock mode.

        :param mode: Interlock mode, where:
                    - 0x01 = SOLENOID_ENABLED (hardware interlock required)
                    - 0x02 = SOLENOID_DISABLED (hardware interlock not required)
        """

        # Send the message with Channel ID in param1 and Interlock Mode in param2
        await self.send(Message(MGMSG.MOT_SET_SOL_INTERLOCKMODE, param2=mode))

    async def get_sol_interlock_mode(self):
        """Get the current solenoid interlock mode.

        :return: The interlock mode, where:
                - 0x01 = SOLENOID_ENABLED (hardware interlock required)
                - 0x02 = SOLENOID_DISABLED (hardware interlock not required)
        """

        # Send the request to get the current interlock mode
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_SOL_INTERLOCKMODE, [MGMSG.MOT_GET_SOL_INTERLOCKMODE], param1=1
        )

        interlock_mode = get_msg.param2

        return interlock_mode

    async def set_sol_state(self, state):
        """Set the solenoid state (ON or OFF).

        :param state: The solenoid state, where:
                    - 0x01 = SOLENOID_ON (solenoid is active).
                    - 0x02 = SOLENOID_OFF (solenoid is deactivated).
        """

        # Send the message with Channel ID in param1 and State in param2
        await self.send(Message(MGMSG.MOT_SET_SOL_STATE, param2=state))

    async def get_sol_state(self):
        """Get the current solenoid state.

        :return: The solenoid state, where:
                - 0x01 = SOLENOID_ON (solenoid is active).
                - 0x02 = SOLENOID_OFF (solenoid is deactivated).
        """

        # Send the request to get the current solenoid state
        get_msg = await self.send_request(
            MGMSG.MOT_REQ_SOL_STATE, [MGMSG.MOT_GET_SOL_STATE], param1=1
        )

        # Return the solenoid state from param2
        return get_msg.param2


class TscSim:
    def module_identify(self):
        pass

    def get_bay_used(self):
        return False

    def set_absolute_position(self, absolute_position):
        self.absolute_position = absolute_position

    def move_stop(self, stop_mode):
        self.stop_mode = stop_mode

    def set_av_modes(self, mode_bits):
        self.mode_bits = mode_bits

    def get_av_modes(self):
        return self.mode_bits

    def set_button_parameters(self, mode, position1, position2, timeout1, timeout2):
        self.mode = mode
        self.position1 = position1
        self.position2 = position2
        self.timeout1 = timeout1
        self.timeout2 = timeout2

    def get_button_parameters(self):
        return (self.mode, self.position1, self.position2, self.timeout1, self.timeout2)

    def set_eeprom_parameters(self, msg_id):
        self.msg_id = msg_id

    def get_status_update(
        self,
    ):  # TODO: not implemented yet for simulation, need to make the framework to mock this data
        return (
            self.position,
            self.encoder_count,
            self.status_bits,
            self.chan_identity_two,
        )

    def set_sol_operating_mode(self, operating_mode):
        self.operating_mode = operating_mode

    def get_sol_operating_mode(self):
        return self.operating_mode

    def set_solenoid_cycle_parameters(self, on_time, off_time, num_cycles):
        self.on_time = on_time
        self.off_time = off_time
        self.num_cycles = num_cycles

    def get_solenoid_cycle_parameters(self):
        return (self.on_time, self.off_time, self.num_cycles)

    def set_sol_interlock_mode(self, mode):
        self.interlock_mode = mode

    def get_sol_interlock_mode(self):
        return self.interlock_mode

    def set_sol_state(self, state):
        self.sol_state = state

    def get_sol_state(self):
        return self.sol_state
