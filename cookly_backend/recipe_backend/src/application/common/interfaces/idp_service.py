from abc import ABC, abstractmethod


class IDPService(ABC):
    @abstractmethod
    async def get_user_data(self): ...
