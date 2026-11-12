from modules.question_generator import _try_local_model

print("=" * 60)
print("FLAN-T5-LARGE MODEL TEST")
print("=" * 60)

context = """
A threat is any incident that could negatively affect an organization
or its information systems.

Cyber threats include malware, phishing, denial-of-service attacks,
cyber warfare, cyber crime, cyber terrorism and cyber espionage.

Cyber warfare involves actions by a nation-state or international
organization to attack or damage another nation's computers
or information networks.
"""

print("\n[1] Model:")
print("google/flan-t5-large")

print("\n[2] Context:")
print(context)

print("\n[3] Loading FLAN-T5-large...")
print("This may take some time the first time.")

result = _try_local_model(
    context=context,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
)

print("\n[4] Generated output:")

if result:
    print(result)
else:
    print("No output was generated.")

print("\n" + "=" * 60)
print("FLAN-T5-LARGE TEST COMPLETED")
print("=" * 60)