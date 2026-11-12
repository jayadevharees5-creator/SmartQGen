# ============================================================
# SMART Q GEN
# MONGODB ATLAS DATABASE CONFIGURATION
# ============================================================

import os

from dotenv import load_dotenv
from pymongo import MongoClient


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# MONGODB URI
# ============================================================

MONGO_URI = os.getenv(
    "MONGODB_URI"
)


if not MONGO_URI:

    raise RuntimeError(
        "MONGODB_URI is missing from .env"
    )


# ============================================================
# CREATE MONGODB CLIENT
# ============================================================

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)


# ============================================================
# DATABASE
# ============================================================

db = client[
    "smart_q_gen"
]


# ============================================================
# COLLECTIONS
# ============================================================

faculty_collection = db[
    "faculty"
]

documents_collection = db[
    "documents"
]

question_papers_collection = db[
    "question_papers"
]


# ============================================================
# CONNECTION TEST
# ============================================================

try:

    client.admin.command(
        "ping"
    )

    print(
        "[DB] MongoDB Atlas connection successful."
    )

    print(
        "[DB] Database:",
        db.name
    )

except Exception as error:

    print(
        "[DB] MongoDB Atlas connection failed:"
    )

    print(
        error
    )

    raise