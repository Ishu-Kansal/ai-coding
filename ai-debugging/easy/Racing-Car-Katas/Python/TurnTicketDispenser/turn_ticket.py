class TurnTicket(object):
    def __init__(self, turnNumber):
        """Store the ticket's sequence number."""
        self.turnNumber = turnNumber

class TurnNumberSequence(object):
    _turnNumber = -1

    @staticmethod
    def next_turn_number():
        """Advance the process-wide sequence from -1 and return the new non-negative ticket number."""
        TurnNumberSequence._turnNumber += 1
        return TurnNumberSequence._turnNumber


class TicketDispenser(object):
    def getTurnTicket(self):
        """Allocate the next process-wide sequence number and return it in a turn ticket."""
        newTurnNumber = TurnNumberSequence.next_turn_number()
        newTurnTicket = TurnTicket(newTurnNumber)
        return newTurnTicket
