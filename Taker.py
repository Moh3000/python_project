# Abstract Base classes module
from abc import ABC, abstractmethod
class Taker(ABC):

    # An attendance-participation taker script should load students first
    @abstractmethod
    def loadStudents(self):
        pass

    # And provide an attendance taking method that generates the sheet files for attendance
    @abstractmethod
    def takeAttendance(self):
        pass

    # And provide a participation taking method that generates the sheet files for participation
    @abstractmethod
    def takeParticipation(self):
        pass
