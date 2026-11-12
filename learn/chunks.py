import re

text = """UNIT 1
CYBER SECURITY

1.1 Cyber Crime
Cyber crime is an illegal activity performed using computers.
Major types include phishing, hacking and identity theft.

1.2 Malware
Malware is malicious software designed to damage computer systems.
Types include virus, worm, trojan and ransomware.

1.3 Network Security
Network security protects computers and networks from attacks.
It uses different security techniques and protocols.
"""


lines = text.splitlines()
current_topic = None
current_text = []

chunks = []

for line in lines:

    line = line.strip()

    if not line:
        continue

    match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)

    if match:

        if current_topic is not None:

            chunks.append({
                "topic": current_topic,
                "text": " ".join(current_text)
            })

        current_topic = match.group(2)

        current_text = []

    else:

        if current_topic is not None:
            current_text.append(line)



if current_topic is not None:

    chunks.append({
        "topic": current_topic,
        "text": " ".join(current_text)
    })

print("CHUNKING RESULT")


for i, chunk in enumerate(chunks, start=1):


    print("CHUNK", i)

    print("Topic:", chunk["topic"])
    print("Text:", chunk["text"])