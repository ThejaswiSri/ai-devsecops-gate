import re
from typing import List, Dict, Any

class DiffParser:
    """Parses raw Git diff text into structured file-level data."""

    @staticmethod
    def parse_patch(diff_text: str) -> List[Dict[str, Any]]:
        files_changed = []
        file_blocks = re.split(r'^diff --git ', diff_text, flags=re.MULTILINE)

        for block in file_blocks:
            if not block.strip():
                continue

            lines = block.split('\n')
            header = lines[0]

            match = re.search(r'a/(.*?) b/(.*)', header)
            if not match:
                continue

            file_path = match.group(2)

            if not file_path.endswith('.py'):
                continue

            added_lines = []
            removed_lines = []

            for line in lines:
                if line.startswith('+') and not line.startswith('+++'):
                    added_lines.append(line[1:])
                elif line.startswith('-') and not line.startswith('---'):
                    removed_lines.append(line[1:])

            files_changed.append({
                "file_path": file_path,
                "added_count": len(added_lines),
                "removed_count": len(removed_lines),
                "added_code": "\n".join(added_lines),
                "removed_code": "\n".join(removed_lines)
            })

        return files_changed