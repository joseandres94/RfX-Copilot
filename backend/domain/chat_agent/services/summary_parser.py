import re
from typing import Dict, Any, List


class SummaryParser:
    """Service to parse markdown to dictionary"""

    @staticmethod
    def parse(markdown: str) -> Dict[str, Any] | str:
        """Parse markdown to dictionary if it has summary structure, otherwise return original string"""
        # Check if it has H1 and Overview to be a summary
        if not (re.search(r'^#\s+', markdown, re.MULTILINE) and re.search(r'^##\s+Overview', markdown, re.MULTILINE)):
            return markdown
        
        header_re = re.compile(r'^(#{1,6})\s*(.+?)\s*$')
        sections: Dict[str, str] = {}
        current: str | None = None
        buf: List[str] = []

        def flush():
            nonlocal buf, current
            if current is None:
                buf = []
                return
            raw = "\n".join(buf).strip()
            if not raw:
                sections[current] = ""
            else:
                bullets = [m.group(1).strip()
                           for m in re.finditer(r'^\s*[-*]\s+(.*\S)\s*$', raw, flags=re.MULTILINE)]
                sections[current] = bullets if bullets else raw
            buf = []

        for line in markdown.splitlines():
            m = header_re.match(line)
            if m:
                flush()
                header_text = m.group(2).strip()
                # Normalize first H1 to "Title" if it's not already "Title"
                if len(m.group(1)) == 1 and current is None and header_text.lower() != "title":
                    current = "Title"
                    buf.append(header_text)  # Use H1 text as title content
                else:
                    current = header_text
            else:
                buf.append(line)

        flush()
        return sections
    
    @staticmethod
    def is_valid(summary: Dict[str, Any] | str) -> bool:
        """Check if summary is valid"""
        if isinstance(summary, str):
            return False
        required_sections = ["Title", "Overview"]
        return all(section in summary for section in required_sections)
