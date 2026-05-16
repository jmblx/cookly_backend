from dataclasses import dataclass

from application.common.base_exceptions import ApplicationError


@dataclass(eq=False)
class FingerprintMismatchException(ApplicationError): ...
