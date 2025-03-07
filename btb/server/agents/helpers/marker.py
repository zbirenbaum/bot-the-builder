from enum import Enum
import weave
import re
from typing import List

class Marker(Enum):
    IMPLEMENTATION = "IMPLEMENTATION"
    DEPENDENCIES = "DEPENDENCIES"
    TESTS = "TESTS"
    ARGUMENTS = "ARGUMENTS"
    ARGUMENT_TYPES = "ARGUMENT_TYPES"
    USAGE = "USAGE"
    MATCH = "MATCH"
    SUMMARY = "SUMMARY"
    ENV_VARIABLES = "ENV_VARIABLES"
    OUTPUT = "OUTPUT"

markers = { m.name: { "start": "# START_" + m.value, "end": "# END_" + m.value } for m in Marker }

@weave.op
def parse_marked_blocks(marker: Marker, contents: str) -> List[str]:
    start = markers[marker.name]["start"]
    end = markers[marker.name]["end"]
    pattern = rf"{start}(?:\w+\s+)?(.*?){end}"
    compiled_pattern = re.compile(pattern, re.DOTALL)
    matches = compiled_pattern.findall(contents)
    return "\n".join([block.strip() for block in matches])
