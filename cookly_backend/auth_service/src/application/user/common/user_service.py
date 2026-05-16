from abc import ABC, abstractmethod

from domain.entities.client.model import Client
from domain.entities.user.model import User


class UserService(ABC):
    @abstractmethod
    async def add_client_to_user(self, user: User, client: Client):
        """
        Needs user with loaded clients. Adds client and client base roles to user.
        """
