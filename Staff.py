class Staff:
    def __init__(self, staffid):
        self._staffid = staffid
        self._status = 'Free'

    @property
    def staffid(self):
        return self._staffid
    
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, status):
        self._status = status
    
    def close(self):
        self._status = 'Closed'
