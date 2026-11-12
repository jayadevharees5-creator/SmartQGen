from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("STRUCTURE DETECTOR TEST")
print("================================")


# 1. Extract document using the original document_processor module
print("\nReading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

print("Source:", extracted_doc["source"])
print("Pages:", len(extracted_doc["pages"]))
print("Characters:", extracted_doc["total_characters"])


# 2. Pass extracted document to the original structure_detector module
print("\nDetecting document structure...")

structure_data = parse_document_structure(extracted_doc)


# 3. Get the output produced by structure_detector
structure_map = structure_data["structure_map"]
detected_chapters = structure_data["detected_chapters"]

print("Structure items:", len(structure_map))


# 4. Display detected chapters
print("\nDetected Chapters:")

for chapter in detected_chapters:
    print("-", chapter)


# 5. Display first few structure items
print("\n================================")
print("STRUCTURE MAP")
print("================================")

for item in structure_map[:10]:

    print("\nPage:", item["page"])
    print("Chapter:", item["chapter"])
    print("Chapter Title:", item["chapter_title"])
    print("Topic:", item["topic"])
    print("Text:", item["text"])


# 6. Final result
print("\n================================")

if structure_map:
    print("STRUCTURE DETECTOR TEST PASSED")
else:
    print("STRUCTURE DETECTOR TEST FAILED")

print("================================")