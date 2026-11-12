from database.mongodb import client, db


try:
    # Test connection
    client.admin.command("ping")
    print("[DB] MongoDB Atlas connection successful!")

    # Insert test document
    result = db["test"].insert_one({
        "message": "Smart Q Gen database is working",
        "test": True
    })

    print("[DB] Test document inserted!")
    print("[DB] Document ID:", result.inserted_id)

    # Read it back
    document = db["test"].find_one({
        "_id": result.inserted_id
    })

    print("[DB] Test document retrieved:")
    print(document)

except Exception as e:
    print("[DB] MongoDB test failed:")
    print(e)