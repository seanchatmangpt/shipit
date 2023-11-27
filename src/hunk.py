import re
from pathlib import Path

from pydantic import BaseModel
from typing import List, Optional


class Hunk(BaseModel):
    startsrc: int
    linessrc: int
    starttgt: int
    linestgt: int
    lines: List[str]


class FileDiff(BaseModel):
    source_file: str
    target_file: str
    hunks: List[Hunk]


class GitPatch(BaseModel):
    diff_files: List[FileDiff]

    def to_patch(self) -> str:
        lines = []
        for diff_file in self.diff_files:
            lines.append("--- " + diff_file.source_file)
            lines.append("+++ " + diff_file.target_file)

            for hunk in diff_file.hunks:
                hunk_header = f"@@ -{hunk.startsrc},{hunk.linessrc} +{hunk.starttgt},{hunk.linestgt} @@"
                lines.append(hunk_header)
                lines.extend(hunk.lines)

        return "\n".join(lines)

    @staticmethod
    def from_patch(file_path: str | Path) -> "GitPatch":
        with open(file_path, "r") as f:
            content = f.read()

        lines = content.split("\n")

        diff_files = []
        current_file = None
        current_hunk = None

        for line in lines:
            if line.startswith("--- "):
                current_file = FileDiff(
                    source_file=line[4:], target_file=None, hunks=[]
                )
                diff_files.append(current_file)

            elif line.startswith("+++ "):
                current_file.target_file = line[4:]

            elif line.startswith("@@"):
                # Start new hunk
                current_hunk = Hunk(lines=[])
                current_file.hunks.append(current_hunk)

                # Parse hunk header
                match = re.match(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@", line)
                if match:
                    current_hunk.startsrc = int(match.group(1))
                    current_hunk.linessrc = int(match.group(2))
                    current_hunk.starttgt = int(match.group(3))
                    current_hunk.linestgt = int(match.group(4))

            else:
                # Collect hunk content
                current_hunk.lines.append(line)

        return GitPatch(diff_files=diff_files)


git_patch = GitPatch.from_patch(
    "/Users/candacechatman/dev/shipit/0001-Hello-World.patch"
)

print(git_patch.to_patch())
