class DomainError(Exception):
    pass


class ValidationFailed(DomainError):
    def __init__(self, message="Validation failed"):
        super().__init__(message)


class SchedulingConflict(DomainError):
    def __init__(self, conflicts):
        self.conflicts = conflicts
        super().__init__("Scheduling conflict")


class NotFound(DomainError):
    pass


class InactiveTechnician(DomainError):
    def __init__(self, technician_id):
        super().__init__(f"Technician {technician_id} is inactive and cannot be scheduled")
        self.technician_id = technician_id
