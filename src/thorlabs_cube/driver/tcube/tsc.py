import struct as st

from thorlabs_cube.driver.base import _Cube
from thorlabs_cube.driver.message import MGMSG, Message, MsgError


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
            or msg_id == MGMSG.MOT_MOVE_STOPPED
            # might need to add one more check, yet to determine
        ):
            if self.status_report_counter == 25:
                self.status_report_counter = 0
                await self.send(Message(MGMSG.MOT_MOVE_COMPLETED))
            # else:
            #     self.status_report_counter += 1
            # # 'r' is a currently unused and reserved field
            # self.position, self.velocity, r, self.status = st.unpack(
            #     "<LHHL",
            #     data[2:],
            # )

    # functions from base class definition start
    
    # def module_identify(self):
    #     return super().module_identify()
    
    def hardware_start_update_messages(self, update_rate):
        return super().hardware_start_update_messages(update_rate)
    
    def hardware_stop_update_messages(self):
        return super().hardware_stop_update_messages()
    
    def is_channel_enabled(self):
        return super().is_channel_enabled()
    
    def ping(self):
        return super().ping()
    
    # functions from base class definition end

    async def identify_used_bay(self):
        get_msg = await self.send_request(
            MGMSG.HUB_REQ_BAYUSED, [MGMSG.MOT_GET_POSCOUNTER], 1
        )
        return st.unpack("<l", get_msg.id[1:])[0] #should give us the bay ident within the header
    
    # async def set_move_absolute(self):
    #     get_msg = await self.send_request(
    #         MGMSG.MOT_MOVE_ABSOLUTE, [MGMSG.MOT_MOVE_COMPLETED],1,
    #     )
    #     return st.unpack("")

class TscSim():
    pass