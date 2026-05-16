from dataclasses import dataclass


@dataclass
class ImageDTO:
    content: bytes
    content_type: str
