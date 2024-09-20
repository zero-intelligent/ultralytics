import time


class UserMonitor:
    # webservice 连接数量
    ws_connection_cnt = 0

    #最后一个用户的离开时间
    ws_last_disconnect_time = None

    @staticmethod
    def user_enter():
        UserMonitor.ws_connection_cnt += 1
    
    @staticmethod
    def user_leave():
        UserMonitor.ws_connection_cnt -= 1
        
        UserMonitor.ws_last_disconnect_time = time.time()  # 记录离开时间
    
    @staticmethod
    def has_active_client(timeout:int = 60):
        return UserMonitor.ws_connection_cnt > 0 \
            or UserMonitor.ws_last_disconnect_time is not None \
            and UserMonitor.ws_last_disconnect_time + timeout > time.time()


