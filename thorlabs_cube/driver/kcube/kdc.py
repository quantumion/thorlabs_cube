import struct as st

from thorlabs_cube.driver.tcube.tdc import Tdc
from thorlabs_cube.driver.message import MGMSG, MsgError, Message


class Kdc(Tdc):
    """
    Controller class for KDC101 K-Cube Brushed DC Servo Motor Controller
    """

    def __init__(self, serial_dev):
        """Initialize from TDC001 control class"""
        super().__init__(serial_dev)

    async def handle_message(self, msg):
        """Parse messages from the device. Minor adaptation from TDC001 method."""
        msg_id = msg.id
        data = msg.data

        if msg_id == MGMSG.HW_DISCONNECT:
            raise MsgError("Error: Please disconnect the KDC101")
        elif msg_id == MGMSG.HW_RESPONSE:
            raise MsgError("Hardware error, please disconnect and reconnect the KDC101")
        elif msg_id == MGMSG.HW_RICHRESPONSE:
            (code, ) = st.unpack("<H", data[2:4])
            raise MsgError(f"Hardware error {code}: {data[4:].decode(encoding="ascii")}")
        elif (msg_id == MGMSG.MOT_MOVE_COMPLETED or
              msg_id == MGMSG.MOT_MOVE_STOPPED or
              msg_id == MGMSG.MOT_GET_DCSTATUSUPDATE):
            if self.status_report_counter == 25:
                self.status_report_counter = 0
                await self.send(Message(MGMSG.MOT_ACK_DCSTATUSUPDATE))
            else:
                self.status_report_counter += 1
            # 'r' is a currently unused and reserved field
            self.position, self.velocity, r, self.status = st.unpack("<LHHL", data[2:])

    async def set_mmi_parameters(self, mode, max_velocity, max_acceleration, direction, position1, position2,
                                 brightness, timeout, dim):
        """Set the operating parameters of the top panel wheel (Joystick).

        :param mode: This parameter specifies the operating mode of the wheel/joy stick as follows:\n
                     * 1: Velocity Control Mode - Deflecting the wheel starts a move with the velocity proportional to
                       the deflection. The maximum velocity (i.e. velocity corresponding to the full deflection of the
                       joystick wheel) and acceleration are specified in the max_velocity and max_acceleration
                       parameters.
                     * 2: Jog Mode - Deflecting the wheel initiates a jog move, using the parameters specified by the
                       set_jog step_size and max_velocity methods. Keeping the wheel deflected repeats the move
                       automatically after the current move has completed.
                     * 3: Go To Position Mode - Deflecting the wheel starts a move from the current position to one of
                       the two predefined “teach” positions. The teach positions are specified in number of steps from
                       the home position in the position1 and position parameters.
        :param max_velocity: The maximum velocity of a move initiated by the top panel velocity wheel.
        :param max_acceleration: The maximum acceleration of a move initiated by the top panel velocity wheel.
        :param direction: This parameter specifies the direction of a move initiated by the velocity wheel as follows:\n
                          * 0: Wheel initiated moves are disabled. Wheel used for menuing only.
                          * 1: Upwards rotation of the wheel results in a positive motion (i.e. increased position
                            count).
                            The following option applies only when the mode is set to Velocity Control Mode (1). If set to
                            Jog Mode (2) or Go to Position Mode (3), the following option is ignored.\n
                          * 2: Upwards rotation of the wheel results in a negative motion (i.e. decreased position
                            count).
        :param position1: The preset position 1 when operating in go to position mode, measured in position steps from
                          the home position.
        :param position2: The preset position 2 when operating in go to position mode, measured in position steps from
                          the home position.
        :param brightness: In certain applications, it may be necessary to adjust the brightness of the LED display on
                           the top of the unit. The brightness is set as a value from 0 (Off) to 100 (brightest). The
                           display can be turned off completely by entering a setting of zero, however, pressing the
                           MENU button on the top panel will temporarily illuminate the display at its lowest brightness
                           setting to allow adjustments. When the display returns to its default position display mode,
                           it will turn off again.
        :param timeout: 'Burn In' of the display can occur if it remains static for a long time. To prevent this, the
                        display is automatically dimmed after the time interval specified in the timeout parameter has
                        elapsed. Set in minutes in the range 0 (never dimmed) to 480. The dim level is set in the
                        dim parameter below.
        :param dim: The dim level, as a value from 0 (Off) to 10 (brightest) but is also limited by the brightness
                    parameter.
        """
        payload = st.pack("<HHllHllHHHH", 1, mode, max_velocity, max_acceleration, direction, position1, position2,
                          brightness, timeout, dim, 0)
        await self.send(Message(MGMSG.MOT_SET_KCUBEMMIPARAMS, data=payload))

    async def get_mmi_parameters(self):
        """Get the operating parameters of the top panel wheel (Joystick).

        :return: A 9 int tuple containing in this order: joystick mode, maximum velocity, maximum acceleration,
                 direction, position1, position2, brightness, timeout, and dim. Cf. :py:meth:`set_mmi_parameters()
                 <Kdc.set_mmi_parameters>` for description.
        :rtype: A 9 int tuple
        """
        get_msg = await self.send_request(MGMSG.MOT_REQ_KCUBEMMIPARAMS, [MGMSG.MOT_GET_KCUBEMMIPARAMS], 1)
        return st.unpack("<HllHllHHH", get_msg.data[2:28])
