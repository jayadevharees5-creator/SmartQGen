
import re
text = """UNIT 1
Introduction to Cyber Security
CHAPTER 2
Network Security
1.1 Malware
Malware is malicious software.
NETWORK SECURITY
Network security protects computers and networks.
1.2 Security Threats
A security threat is a potential danger.
"""
lines = text.splitlines()

unit_pattern = r"^UNIT\s+\d+$"
chapter_pattern = r"^CHAPTER\s+\d+$"
section_pattern = r"^\d+\.\d+\s+.+$"

structure_data = []

for line_number, line in enumerate(lines, start=1):

    line = line.strip()


    if not line:
        continue

    

    if re.match(unit_pattern, line, re.IGNORECASE):

        structure_data.append({
            "line_number": line_number,
            "type": "UNIT",
            "text": line
        })


    elif re.match(chapter_pattern, line, re.IGNORECASE):

        structure_data.append({
            "line_number": line_number,
            "type": "CHAPTER",
            "text": line
        })


    elif re.match(section_pattern, line):

        structure_data.append({
            "line_number": line_number,
            "type": "SECTION",
            "text": line
        })


    elif (
        len(line) < 60
        and line.isupper()
        and not line.endswith(".")
    ):

        structure_data.append({
            "line_number": line_number,
            "type": "HEADING",
            "text": line
        })


    else:

        structure_data.append({
            "line_number": line_number,
            "type": "TEXT",
            "text": line
        })



print("STORED STRUCTURE DATA")


for item in structure_data:
    print(item)