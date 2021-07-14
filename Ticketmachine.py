import datetime
from Ticket import Ticket
from Staff import Staff

class Ticketmachine():
    def __init__(self):
        self._queue = []  # Tickets in queue
        self._items = []  # All tickets
        self._staffmembers = []

    def create_ticket(self, discord_id):
        # Generate a new ticketnumber
        if len(self._items) == 0:
            tn = 1111111
        else:
            tn = self._items[-1].ticketnumber + 1
        # Create Ticket
        ticket = Ticket(tn, discord_id)
        self._queue.append(ticket)
        self._items.append(ticket)
        place_in_queue = len(self._queue)
        return (ticket.ticketnumber, place_in_queue)
  
    def handle_ticket(self, staffid):
        # Check if there are tickets
        if len(self._queue) == 0:
            print(self._queue)
            return None
        # Get the staff
        staff = None
        for staffmember in self._staffmembers:
            if staffmember.staffid == staffid:
                staff = staffmember
        if staff == None: 
            print(self._staffmembers)
            return None
        # Assign the question
        staff.status = 'Handling'
        ticket = self._queue.pop(0)
        ticket.assign(staff)
        return (ticket.ticketnumber, ticket.userid)

    def close_ticket(self, ticketnumber):
        # Find the ticket
        ticket = None
        for t in self._items:
            if t.ticketnumber == ticketnumber:
                ticket = t
        if ticket == None:
            return None
        # Remove from queue
        self._queue.remove(ticket)
        # Close the Ticket
        ticket.close()

    def finish_ticket(self, ticketnumber, messages):
        # Find the ticket
        ticket = None
        for t in self._items:
            if t.ticketnumber == ticketnumber:
                ticket = t
        if ticket == None: return False
        # Close the Ticket
        if ticket.status == 'Handling':
            ticket.close()
            staff = ticket._staffmember
            staff._status = 'Free'
        else:
            return False
        # Save the messages
        ticket._questions_and_response = messages
        return (ticket.userid, ticket.staffid)
    
    def information_ticket(self, ticketnumber):
        # Find the ticket
        ticket = None
        for t in self._items:
            if t.ticketnumber == ticketnumber:
                ticket = t
        if ticket == None: return None
        # Return all the information of the ticketnumber
        return {'user' : ticket.userid, 'staff' : ticket.staffid, 'status' : ticket.status, 'date' : ticket.date, 'duration' : ticket.duration, 'questions' : ticket.questions}

    def add_staff(self, staffid):
        if not staffid in [ staff.staffid for staff in self._staffmembers]:
            staff = Staff(staffid)
            self._staffmembers.append(staff)
    def delete_staff(self, staffid):
        for member in self._staffmembers:
            if member.staffid == staffid:
                member.close()
            
    @property
    def isEmpty(self):
        return self._queue == []
    @property
    def size(self):
        return len(self._queue)
    @property
    def list(self):
        return self._queue

    def already_in_queue(self, discord_id):
        current_ticket = None
        for ticket in self._queue:
            if discord_id == ticket.userid:
                current_ticket = ticket
                break
        if current_ticket == None: return None
        return (current_ticket.ticketnumber, self._queue.index(current_ticket) + 1)
