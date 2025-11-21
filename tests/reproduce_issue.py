
import sys
import os
from pathlib import Path

# Add the project root to the python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from cli.main import MessageBuffer, extract_content_string

def test_update_report_section_with_list():
    print("Testing MessageBuffer.update_report_section with list content...")
    buffer = MessageBuffer()
    
    # Simulate Anthropic-style list content
    list_content = [
        {"type": "text", "text": "This is a report part 1."},
        {"type": "text", "text": " This is report part 2."}
    ]
    
    try:
        buffer.update_report_section("market_report", list_content)
        print("Successfully updated report section.")
    except Exception as e:
        print(f"FAILED: Exception raised: {e}")
        sys.exit(1)
        
    # Verify the content is a string
    stored_content = buffer.report_sections["market_report"]
    if isinstance(stored_content, str):
        print(f"SUCCESS: Stored content is a string: '{stored_content}'")
        if stored_content == "This is a report part 1.  This is report part 2.":
             print("Content matches expected string.")
        else:
             print(f"WARNING: Content content mismatch. Got: '{stored_content}'")
    else:
        print(f"FAILED: Stored content is not a string. Type: {type(stored_content)}")
        sys.exit(1)

if __name__ == "__main__":
    test_update_report_section_with_list()
