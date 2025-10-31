class SuccessResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self.data = data


class FailedResponse:
    def __init__(self, status_code=400, detail=None):
        self.status_code = status_code
        self.detail = detail
