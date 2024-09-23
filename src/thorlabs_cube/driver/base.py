import asyncio
import logging
import struct as st

import asyncserial

from thorlabs_cube.driver.message import MGMSG, Message, MsgError

logger = logging.getLogger(__name__)


class _Cube:
    def __init__(self, loop, serial_dev):
        """Initialize the _Cube base class.

        Parameters:
            loop: The event loop to use for asynchronous operations.
            serial_dev: The serial device (e.g., port) to connect to.
        """
        self.port = asyncserial.Serial(loop, serial_dev, baudrate=115200, rtscts=True)

    async def close(self):
        """Close the device."""
        await self.port.close()

    async def send(self, message):
        """Send a message to the device.

        Parameters:
            message (Message): The message object to send.
        """
        logger.debug("sending: %s", message)
        await self.port.write(message.pack())

    async def recv(self):
        """Receive a message from the device.

        Waits for a message from the device, reads and unpacks it.

        Returns:
            Message: The message object received from the device.
        """
        header = await self.port.read(num_bytes=6)
        logger.debug("received header: %s", header)
        data = b""
        if header[4] & 0x80:
            (length,) = st.unpack("<H", header[2:4])
            data = await self.port.read(num_bytes=length)
        r = Message.unpack(header + data)
        logger.debug("receiving: %s", r)
        return r

    async def handle_message(self, msg):
        """Handle an incoming message.

        This method should be implemented by derived classes to process incoming messages.

        Parameters:
            msg (Message): The message object received from the device.

        Raises:
            NotImplementedError: If not implemented in derived class.
        """
        # derived classes must implement this
        raise NotImplementedError

    async def send_request(
        self, msgreq_id, wait_for_msgs, param1=0, param2=0, data=None
    ):
        """Send a request message and wait for a response.

        Sends a request message and waits until a response with an expected message ID is received.

        Parameters:
            msgreq_id (MGMSG): The message ID to send as a request.
            wait_for_msgs (list of MGMSG): A list of message IDs to wait for in the response.
            param1 (int, optional): The first parameter for the message. Defaults to 0.
            param2 (int, optional): The second parameter for the message. Defaults to 0.
            data (bytes, optional): Any additional data to include in the message. Defaults to None.

        Returns:
            Message: The received message that matches one of the IDs in wait_for_msgs.
        """
        await self.send(Message(msgreq_id, param1, param2, data=data))
        msg = None
        while msg is None or msg.id not in wait_for_msgs:
            msg = await self.recv()
            await self.handle_message(msg)
        return msg

    async def set_channel_enable_state(self, activated):
        """Enable or Disable channel 1.

        :param activated: 1 to enable channel, 0 to disable it.
        """

        if activated:
            activated = 1
        else:
            activated = 2

        await self.send(
            Message(MGMSG.MOD_SET_CHANENABLESTATE, param1=1, param2=activated)
        )

    async def get_channel_enable_state(self):
        """Get the enable state of the channel.

        Requests and retrieves the channel enable state from the device.

        Returns:
            bool: True if the channel is enabled, False if disabled.

        Raises:
            MsgError: If the response is invalid.
        """
        get_msg = await self.send_request(
            MGMSG.MOD_REQ_CHANENABLESTATE, [MGMSG.MOD_GET_CHANENABLESTATE], 1
        )
        self.chan_enabled = get_msg.param2
        if self.chan_enabled == 1:
            self.chan_enabled = True
        elif self.chan_enabled == 2:
            self.chan_enabled = False
        else:
            raise MsgError(
                "Channel state response is invalid: neither "
                "1 nor 2: {}".format(self.chan_enabled)
            )
        return self.chan_enabled

    async def module_identify(self):
        """Ask device to flash its front panel led.

        Instruct hardware unit to identify itself by flashing its front panel
        led.
        """
        await self.send(Message(MGMSG.MOD_IDENTIFY))

    async def hardware_start_update_messages(self, update_rate):
        """Start status updates from the embedded controller.

        Status update messages contain information about the position and
        status of the controller.

        :param update_rate: Rate at which you will receive status updates
        """
        await self.send(Message(MGMSG.HW_START_UPDATEMSGS, param1=update_rate))

    async def hardware_stop_update_messages(self):
        """Stop status updates from the controller."""
        await self.send(Message(MGMSG.HW_STOP_UPDATEMSGS))

    async def hardware_request_information(self):
        """Request hardware information from the device.

        Sends a request for hardware information and waits for the response.

        Returns:
            Message: The hardware information message received.
        """
        return await self.send_request(MGMSG.HW_REQ_INFO, [MGMSG.HW_GET_INFO])

    def is_channel_enabled(self):
        """Check if the channel is enabled.

        Returns:
            bool: The current enable state of the channel.
        """
        return self.chan_enabled

    async def ping(self):
        """Check if the device is responsive.

        Attempts to communicate with the device to confirm it is responsive.

        Returns:
            bool: True if the device responded, False otherwise.
        """
        try:
            await self.hardware_request_information()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("ping failed", exc_info=True)
            return False
        return True