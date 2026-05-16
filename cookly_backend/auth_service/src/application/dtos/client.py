from dataclasses import dataclass


@dataclass(frozen=True)
class ClientCreateDTO:
    client_id: int
