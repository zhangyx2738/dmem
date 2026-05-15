from dataclasses import dataclass, field
from typing import List

@dataclass
class GenieSpaceConfig:
    space_id: str
    name: str
    description: str
    keywords: List[str] = field(default_factory=list)

GENIE_SPACES = [
    GenieSpaceConfig(
        space_id="01f14fd33f431c5fbb9b3bb6a8a39d57",
        name="DMEM Audit",
        description=(
            """This space provides data that should be filtered by buying groups (a combination of chain_id, nationalgroup, and account classification code)."""
        ),
        keywords=[],
    ),
]

GENIE_SPACE_MAP = {gs.name: gs for gs in GENIE_SPACES}

# LLM Configuration
LLM_ENDPOINT = "databricks-claude-sonnet-4-5"