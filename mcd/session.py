import time


class UserMonitor:
    # webservice 连接数量
    ws_connection_cnt = 0

    #最后一个用户的离开时间
    ws_last_disconnect_time = None

    @classmethod
    def user_enter(cls):
        cls.ws_connection_cnt += 1
    
    @classmethod
    def user_leave(cls):
        cls.ws_connection_cnt -= 1
        
        cls.ws_last_disconnect_time = time.time()  # 记录离开时间
    
    @classmethod
    def has_active_client(cls,timeout:int = 60):
        return cls.ws_connection_cnt > 0 \
            or cls.ws_last_disconnect_time is not None \
            and cls.ws_last_disconnect_time + timeout > time.time()


