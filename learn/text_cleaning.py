import re
text = "This is a sample text with    extra spaces and newlines."

print("before cleaning:", text)

text = re.sub(r"\s+", " ", text)  # Remove extra whitespace

print("after cleaning:", text)