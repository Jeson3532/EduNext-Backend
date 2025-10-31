from typing import Union, Optional


def fail_response(status_code=200, detail: Union[str, dict] = None):
    return {'success': False, 'status_code': status_code, 'detail': detail}


def success_response(status_code=200, data: Optional[Union[str, dict]] = None):
    return {'success': True, 'status_code': status_code, 'data': data}
