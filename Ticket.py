import datetime
  
class Ticket():
    def __init__(self, ticketnumber, userid):
        self._ticketnumber = ticketnumber
        self._staffmember = None
        self._userid = userid
        self._questions_and_response = None
        self.open()
    
    def assign(self, staff):
        self._staffmember = staff
        self._status = 'Handling'

    def open(self):
        self._status = 'Open'
        self._date = datetime.datetime.now()
        self._duration = None

    def close(self):
        self._status = 'Closed'
        self._duration = datetime.datetime.now() - self._date
        
    @property
    def status(self):
        return self._status

    @property
    def ticketnumber(self):
        return self._ticketnumber

    @property
    def userid(self):
        return self._userid
    @userid.setter
    def userid(self, discord_id):
        self._userid = discord_id

    @property
    def staffid(self):
        if self._staffmember == None:
            return None
        return self._staffmember.staffid

    @property
    def date(self):
        return self._date

    @property
    def duration(self):
        return self._duration

    @property
    def questions(self):
        return self._questions_and_response
    @questions.setter
    def questions(self, questions):
        self._questions_and_response = questions
        

  
  


  
