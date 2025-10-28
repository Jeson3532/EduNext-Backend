from typing import Union, Optional


def fail_response(status_code, detail: Union[str, dict]):
    return {'success': False, 'status_code': status_code, 'detail': detail}


def success_response(status_code, data: Optional[Union[str, dict]]):
    return {'success': True, 'status_code': status_code, 'data': data}
