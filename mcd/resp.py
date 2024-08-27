def ok(data=None,msg = 'success'):
    if data:
        return {
            'code': 0,
            'data': data,
            'msg':msg
        }
    else:
        return {
            'code': 0,
            'msg':msg
        }
        
def error(code=1,msg='fail'):
    return {
        'code': code,
        'msg':msg
    }