from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ImageEntry:
    index: int
    path: Path
    caption: str = "подпись к рисунку"


@dataclass
class SectionContent:
    text: str = ""
    images: List[ImageEntry] = field(default_factory=list)

