
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    session,
    redirect
)

from werkzeug.utils import secure_filename

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from dotenv import load_dotenv

from datetime import datetime, timezone

from bson import ObjectId

import os
import uuid
load_dotenv()
from database.mongodb import (
    faculty_collection,
    documents_collection,
    question_papers_collection
)

from modules.document_processor import extract_document

from modules.structure_detector import (
    parse_document_structure
)

from modules.chunker import (
    create_chunks_from_structure
)

from modules.question_paper_generator import (
    generate_question_paper
)

from modules.pdf_exporter import (
    generate_question_paper_pdf
)
app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="static",
    static_url_path="/static"
)

FLASK_SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY"
)

if not FLASK_SECRET_KEY:

    raise RuntimeError(
        "FLASK_SECRET_KEY is missing from .env"
    )

app.secret_key = FLASK_SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = False

UPLOAD_FOLDER = "uploads"

PDF_FOLDER = os.path.join(
    "generated",
    "pdf"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["PDF_FOLDER"] = PDF_FOLDER
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    PDF_FOLDER,
    exist_ok=True
)
ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


def allowed_file(filename):
    """
    Check whether the uploaded file
    has a supported extension.
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return extension in ALLOWED_EXTENSIONS

def login_required():
    """
    Return True when a faculty member
    has an active Flask session.
    """

    return bool(
        session.get("faculty_id")
    )


def get_current_faculty_id():
    """
    Return the currently logged-in
    faculty MongoDB ID.
    """

    faculty_id = session.get(
        "faculty_id"
    )

    if not faculty_id:
        return None

    return faculty_id


def get_current_faculty():
    """
    Retrieve the currently logged-in
    faculty record from MongoDB.
    """

    faculty_id = get_current_faculty_id()

    if not faculty_id:
        return None

    try:

        return faculty_collection.find_one({
            "_id": ObjectId(faculty_id)
        })

    except Exception as error:

        print(
            "[AUTH] Could not retrieve faculty:",
            error
        )

        return None


@app.route("/")
def home():

    if login_required():

        return redirect(
            "/dashboard"
        )

    return render_template(
        "login.html"
    )

# LOGIN PAGE

@app.route(
    "/login",
    methods=["GET"]
)
def login_page():

    if login_required():

        return redirect(
            "/dashboard"
        )

    return render_template(
        "login.html"
    )



# FACULTY LOGIN API

@app.route(
    "/login",
    methods=["POST"]
)
def login_api():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "success": False,
                "error":
                    "No login data was received."
            }), 400


       
        # GET LOGIN VALUES

        username = str(
            data.get(
                "username",
                ""
            )
        ).strip()

        password = str(
            data.get(
                "password",
                ""
            )
        )


       
        # VALIDATION
   
        if not username:

            return jsonify({
                "success": False,
                "error":
                    "Username is required."
            }), 400


        if not password:

            return jsonify({
                "success": False,
                "error":
                    "Password is required."
            }), 400


       
        # FIND FACULTY
      

        faculty = faculty_collection.find_one({
            "username": username
        })


        if not faculty:

            return jsonify({
                "success": False,
                "error":
                    "Invalid username or password."
            }), 401


       
        # CHECK PASSWORD
      

        password_hash = faculty.get(
            "password_hash",
            ""
        )


        if not password_hash:

            return jsonify({
                "success": False,
                "error":
                    "Faculty account is not configured correctly."
            }), 500


        if not check_password_hash(
            password_hash,
            password
        ):

            return jsonify({
                "success": False,
                "error":
                    "Invalid username or password."
            }), 401


       
        # CREATE SESSION
        
        session.clear()


    
        session["faculty_id"] = str(
            faculty["_id"]
        )


        session["faculty_username"] = (
            faculty.get(
                "username",
                username
            )
        )


        session["faculty_name"] = (
            faculty.get(
                "name",
                ""
            )
        )


        print()

        print(
            "[AUTH] Faculty login successful."
        )

        print(
            "[AUTH] Username:",
            username
        )

        print(
            "[AUTH] Faculty ID:",
            faculty["_id"]
        )


        return jsonify({

            "success": True,

            "message":
                "Login successful. Redirecting...",

            "username":
                faculty.get(
                    "username",
                    username
                ),

            "name":
                faculty.get(
                    "name",
                    ""
                )

        })


    except Exception as error:

        print(
            "[AUTH] Login error:",
            error
        )

        return jsonify({

            "success": False,

            "error":
                "Login failed. Please try again."

        }), 500


# ============================================================
# REGISTER PAGE
# ============================================================

@app.route(
    "/register",
    methods=["GET"]
)
def register_page():

    if login_required():

        return redirect(
            "/dashboard"
        )

    return render_template(
        "register.html"
    )


# ============================================================
# FACULTY REGISTRATION API
# ============================================================

@app.route(
    "/register",
    methods=["POST"]
)
def register_api():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({
                "success": False,
                "error":
                    "No registration data was received."
            }), 400


        # ----------------------------------------------------
        # GET VALUES
        # ----------------------------------------------------

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()


        username = str(
            data.get(
                "username",
                ""
            )
        ).strip()


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        confirm_password = str(
            data.get(
                "confirmPassword",
                ""
            )
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name:

            return jsonify({
                "success": False,
                "error":
                    "Faculty name is required."
            }), 400


        if not username:

            return jsonify({
                "success": False,
                "error":
                    "Username is required."
            }), 400


        if len(username) < 3:

            return jsonify({
                "success": False,
                "error":
                    "Username must contain at least 3 characters."
            }), 400


        if not email:

            return jsonify({
                "success": False,
                "error":
                    "Email address is required."
            }), 400


        if not password:

            return jsonify({
                "success": False,
                "error":
                    "Password is required."
            }), 400


        if len(password) < 6:

            return jsonify({
                "success": False,
                "error":
                    "Password must contain at least 6 characters."
            }), 400


        if password != confirm_password:

            return jsonify({
                "success": False,
                "error":
                    "Passwords do not match."
            }), 400


        # ----------------------------------------------------
        # CHECK USERNAME
        # ----------------------------------------------------

        existing_username = (
            faculty_collection.find_one({
                "username": username
            })
        )


        if existing_username:

            return jsonify({
                "success": False,
                "error":
                    "Username already exists."
            }), 409


        # ----------------------------------------------------
        # CHECK EMAIL
        # ----------------------------------------------------

        existing_email = (
            faculty_collection.find_one({
                "email": email
            })
        )


        if existing_email:

            return jsonify({
                "success": False,
                "error":
                    "An account with this email already exists."
            }), 409


        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = (
            generate_password_hash(
                password
            )
        )


        # ----------------------------------------------------
        # CREATE FACULTY DOCUMENT
        # ----------------------------------------------------

        faculty_document = {

            "name":
                name,

            "username":
                username,

            "email":
                email,

            "password_hash":
                password_hash,

            "created_at":
                datetime.now(
                    timezone.utc
                )

        }


        # ----------------------------------------------------
        # INSERT INTO MONGODB
        # ----------------------------------------------------

        result = (
            faculty_collection.insert_one(
                faculty_document
            )
        )


        print()

        print(
            "[AUTH] Faculty registered successfully."
        )

        print(
            "[AUTH] Username:",
            username
        )

        print(
            "[AUTH] Faculty ID:",
            result.inserted_id
        )


        return jsonify({

            "success":
                True,

            "message":
                "Faculty account created successfully. Please login.",

            "username":
                username,

            "faculty_id":
                str(
                    result.inserted_id
                )

        })


    except Exception as error:

        print(
            "[AUTH] Registration error:",
            error
        )

        return jsonify({

            "success":
                False,

            "error":
                "Registration failed. Please try again."

        }), 500


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout",
    methods=["POST"]
)
def logout():

    username = session.get(
        "faculty_username"
    )

    faculty_id = session.get(
        "faculty_id"
    )


    session.clear()


    print(
        "[AUTH] Faculty logged out:",
        username
    )

    print(
        "[AUTH] Faculty ID:",
        faculty_id
    )


    return jsonify({

        "success":
            True,

        "message":
            "Logged out successfully."

    })


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():

        return redirect(
            "/login"
        )


    return render_template(
        "dashboard.html"
    )


# ============================================================
# RESULT PAGE
# ============================================================

@app.route("/result")
def result():

    if not login_required():

        return redirect(
            "/login"
        )


    return render_template(
        "result.html"
    )


# ============================================================
# GENERATE QUESTION PAPER
# ============================================================

@app.route(
    "/generate",
    methods=["POST"]
)
def generate():

    if not login_required():

        return jsonify({

            "success":
                False,

            "error":
                "Please login before generating a question paper."

        }), 401


    # Get logged-in faculty ID.
    faculty_id = get_current_faculty_id()


    if not faculty_id:

        return jsonify({

            "success":
                False,

            "error":
                "Faculty session is invalid. Please login again."

        }), 401


    file_path = None


    try:

        print()

        print(
            "========================================"
        )

        print(
            "SMART Q GEN"
        )

        print(
            "QUESTION PAPER GENERATION STARTED"
        )

        print(
            "Faculty:",
            session.get(
                "faculty_username"
            )
        )

        print(
            "Faculty ID:",
            faculty_id
        )

        print(
            "========================================"
        )


        # ====================================================
        # 1. GET FILE
        # ====================================================

        uploaded_file = request.files.get(
            "file"
        )


        if uploaded_file is None:

            return jsonify({

                "success":
                    False,

                "error":
                    "No document was uploaded."

            }), 400


        if not uploaded_file.filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "Please select a document."

            }), 400


        original_filename = (
            uploaded_file.filename
        )


        print(
            "[1] Uploaded file:",
            original_filename
        )


        # ====================================================
        # 2. CHECK FILE TYPE
        # ====================================================

        if not allowed_file(
            original_filename
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Unsupported file type. "
                    "Please upload PDF, DOCX or TXT."

            }), 400


        # ====================================================
        # 3. SECURE FILE NAME
        # ====================================================

        safe_filename = secure_filename(
            original_filename
        )


        if not safe_filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "Invalid file name."

            }), 400


        # ====================================================
        # 4. UNIQUE FILE NAME
        # ====================================================

        unique_id = (
            uuid.uuid4().hex[:8]
        )


        name, extension = (
            os.path.splitext(
                safe_filename
            )
        )


        stored_filename = (
            f"{name}_{unique_id}{extension}"
        )


        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            stored_filename
        )


        uploaded_file.save(
            file_path
        )


        print(
            "[1] Saved to:",
            file_path
        )


        # ====================================================
        # 5. GET FORM SETTINGS
        # ====================================================

        subject = request.form.get(
            "subject",
            ""
        ).strip()


        institution = request.form.get(
            "institution",
            ""
        ).strip()


        max_marks = request.form.get(
            "max_marks",
            ""
        ).strip()


        time_allowed = request.form.get(
            "time_allowed",
            ""
        ).strip()


        num_questions_raw = (
            request.form.get(
                "num_questions",
                "5"
            ).strip()
        )


        question_type = (
            request.form.get(
                "question_type",
                "MCQ"
            ).strip()
        )


        difficulty = (
            request.form.get(
                "difficulty",
                "Medium"
            ).strip()
        )


        bloom_level = (
            request.form.get(
                "bloom_level",
                "Understand"
            ).strip()
        )


        print()

        print(
            "[2] QUESTION PAPER SETTINGS"
        )

        print(
            "Subject:",
            subject
        )

        print(
            "Institution:",
            institution
        )

        print(
            "Maximum Marks:",
            max_marks
        )

        print(
            "Time Allowed:",
            time_allowed
        )

        print(
            "Number of Questions:",
            num_questions_raw
        )

        print(
            "Question Type:",
            question_type
        )

        print(
            "Difficulty:",
            difficulty
        )

        print(
            "Bloom Level:",
            bloom_level
        )


        # ====================================================
        # 6. VALIDATE NUMBER OF QUESTIONS
        # ====================================================

        try:

            num_questions = int(
                num_questions_raw
            )

        except (
            ValueError,
            TypeError
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Number of questions must be an integer."

            }), 400


        if num_questions <= 0:

            return jsonify({

                "success":
                    False,

                "error":
                    "Number of questions must be greater than zero."

            }), 400


        if num_questions > 100:

            return jsonify({

                "success":
                    False,

                "error":
                    "Maximum 100 questions are allowed."

            }), 400


        # ====================================================
        # 7. EXTRACT DOCUMENT
        # ====================================================

        print()

        print(
            "[3] READING DOCUMENT..."
        )


        extracted_doc = extract_document(
            file_path
        )


        if not extracted_doc:

            return jsonify({

                "success":
                    False,

                "error":
                    "Unable to extract text from the document."

            }), 400


        # ====================================================
        # 8. DOCUMENT INFORMATION
        # ====================================================

        pages = extracted_doc.get(
            "pages",
            []
        )


        page_count = len(
            pages
        )


        total_characters = int(
            extracted_doc.get(
                "total_characters",
                0
            ) or 0
        )


        print(
            "[3] Pages:",
            page_count
        )


        print(
            "[3] Characters:",
            total_characters
        )


        # ====================================================
        # 9. CHECK TEXT
        # ====================================================

        if total_characters <= 0:

            return jsonify({

                "success":
                    False,

                "error":
                    "No text could be extracted from the document."

            }), 400


        status_message = (
            extracted_doc.get(
                "status_message"
            )
        )


        if status_message:

            print(
                "[3] Status:",
                status_message
            )


        # ====================================================
        # 10. STRUCTURE DETECTION
        # ====================================================

        print()

        print(
            "[4] DETECTING DOCUMENT STRUCTURE..."
        )


        structure_data = (
            parse_document_structure(
                extracted_doc
            )
        )


        if not structure_data:

            return jsonify({

                "success":
                    False,

                "error":
                    "Unable to detect the structure of the uploaded document."

            }), 400


        structure_items = (
            structure_data.get(
                "structure_map",
                []
            )
        )


        detected_chapters = (
            structure_data.get(
                "detected_chapters",
                []
            )
        )


        detected_units = (
            structure_data.get(
                "detected_units",
                []
            )
        )


        detected_topics = (
            structure_data.get(
                "detected_topics",
                []
            )
        )


        print(
            "[4] Structure items:",
            len(structure_items)
        )


        print(
            "[4] Chapters:",
            detected_chapters
        )


        print(
            "[4] Units:",
            detected_units
        )


        print(
            "[4] Topics:",
            detected_topics
        )


        # ====================================================
        # IMPORTANT
        #
        # No manual Unit / Topic / Chapter selection.
        # These are internal metadata only.
        # ====================================================


        # ====================================================
        # 11. CREATE CHUNKS
        # ====================================================

        print()

        print(
            "[5] CREATING DOCUMENT CHUNKS..."
        )


        chunks = (
            create_chunks_from_structure(
                extracted_doc,
                structure_data
            )
        )


        if not chunks:

            return jsonify({

                "success":
                    False,

                "error":
                    "No usable text chunks were created."

            }), 400


        print(
            "[5] Total chunks:",
            len(chunks)
        )


        # ====================================================
        # 12. BUILD RETRIEVAL QUERY
        # ====================================================

        if subject:

            query = subject

        else:

            preview_parts = []


            for page in pages[:3]:

                if not isinstance(
                    page,
                    dict
                ):
                    continue


                page_text = str(
                    page.get(
                        "text",
                        ""
                    )
                ).strip()


                if page_text:

                    preview_parts.append(
                        page_text
                    )


            query = " ".join(
                preview_parts
            )


            query = (
                query[:2000]
                .strip()
            )


        if not query:

            query = (
                "important concepts definitions "
                "principles methods applications "
                "key information"
            )


        print()

        print(
            "[6] RETRIEVAL QUERY:"
        )

        print(
            query
        )


        # ====================================================
        # 13. GENERATE QUESTION PAPER
        # ====================================================

        print()

        print(
            "[7] GENERATING QUESTION PAPER..."
        )


        paper = generate_question_paper(

            chunks=chunks,

            num_questions=num_questions,

            q_type=question_type,

            difficulty=difficulty,

            bloom_level=bloom_level,

            query=query,

            retrieval_top_k=10
        )


        # ====================================================
        # 14. CHECK PAPER
        # ====================================================

        if not paper:

            return jsonify({

                "success":
                    False,

                "error":
                    "Question paper generation failed."

            }), 500


        # ====================================================
        # 15. ADD PAPER METADATA
        # ====================================================

        paper["subject"] = subject

        paper["institution"] = institution

        paper["max_marks"] = max_marks

        paper["time_allowed"] = time_allowed

        paper["num_questions"] = num_questions

        paper["source_document"] = (
            original_filename
        )

        paper["document_pages"] = (
            page_count
        )

        paper["document_chunks"] = (
            len(chunks)
        )


        # ====================================================
        # 16. GENERATION INFORMATION
        # ====================================================

        generated_questions = (
            paper.get(
                "questions",
                []
            )
        )


        generated_count = len(
            generated_questions
        )


        print()

        print(
            "[8] GENERATION RESULT"
        )

        print(
            "Requested:",
            num_questions
        )

        print(
            "Generated:",
            generated_count
        )

        print(
            "Success:",
            paper.get(
                "success",
                False
            )
        )


        # ====================================================
        # 17. SAVE DOCUMENT METADATA
        # ====================================================

        try:

            documents_collection.insert_one({

                "filename":
                    original_filename,

                "stored_filename":
                    stored_filename,

                "subject":
                    subject,

                "faculty_id":
                    faculty_id,

                "document_pages":
                    page_count,

                "document_chunks":
                    len(chunks),

                "uploaded_at":
                    datetime.now(
                        timezone.utc
                    )

            })


            print(
                "[DB] Document metadata saved."
            )


        except Exception as db_error:

            print(
                "[DB] Document metadata save failed:",
                db_error
            )


        # ====================================================
        # 18. SAVE QUESTION PAPER
        # ====================================================

        if generated_questions:

            try:

                question_papers_collection.insert_one({

                    "subject":
                        subject,

                    "institution":
                        institution,

                    "max_marks":
                        max_marks,

                    "time_allowed":
                        time_allowed,

                    "number_questions":
                        num_questions,

                    "question_type":
                        question_type,

                    "difficulty":
                        difficulty,

                    "bloom_level":
                        bloom_level,

                    "questions":
                        generated_questions,

                    "source_document":
                        original_filename,

                    "faculty_id":
                        faculty_id,

                    "created_at":
                        datetime.now(
                            timezone.utc
                        )

                })


                print(
                    "[DB] Question paper saved."
                )


            except Exception as db_error:

                print(
                    "[DB] Question paper save failed:",
                    db_error
                )


        # ====================================================
        # 19. RETURN RESULT
        # ====================================================

        print()

        print(
            "========================================"
        )

        print(
            "QUESTION PAPER GENERATION COMPLETED"
        )

        print(
            "========================================"
        )


        return jsonify({

            "success":
                bool(
                    paper.get(
                        "success",
                        False
                    )
                ),

            "paper":
                paper

        })


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        print()

        print(
            "========================================"
        )

        print(
            "QUESTION PAPER GENERATION ERROR"
        )

        print(
            "========================================"
        )


        print(
            "Error Type:",
            type(error).__name__
        )


        print(
            "Error:",
            str(error)
        )


        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


    finally:

        # ====================================================
        # REMOVE TEMPORARY UPLOAD
        # ====================================================

        if file_path:

            try:

                if os.path.exists(
                    file_path
                ):

                    os.remove(
                        file_path
                    )


                    print(
                        "[CLEANUP] Temporary uploaded file removed."
                    )


            except Exception as cleanup_error:

                print(
                    "[CLEANUP] Could not remove temporary file:",
                    cleanup_error
                )


# ============================================================
# SAVE / DOWNLOAD PDF
# ============================================================

@app.route(
    "/save-pdf",
    methods=["POST"]
)
def save_pdf():

    if not login_required():

        return jsonify({

            "success":
                False,

            "error":
                "Please login before downloading the PDF."

        }), 401


    try:

        print()

        print(
            "========================================"
        )

        print(
            "PDF GENERATION STARTED"
        )

        print(
            "========================================"
        )


        # ====================================================
        # GET JSON
        # ====================================================

        paper_data = request.get_json(
            silent=True
        )


        if not paper_data:

            return jsonify({

                "success":
                    False,

                "error":
                    "No question paper data was received."

            }), 400


        # ====================================================
        # GET PAPER
        # ====================================================

        if (

            isinstance(
                paper_data,
                dict
            )

            and isinstance(
                paper_data.get(
                    "paper"
                ),
                dict
            )

        ):

            paper_data = paper_data["paper"]


        questions = paper_data.get(
            "questions",
            []
        )


        if not isinstance(
            questions,
            list
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Invalid question paper format."

            }), 400


        if not questions:

            return jsonify({

                "success":
                    False,

                "error":
                    "The question paper contains no questions."

            }), 400


        print(
            "[1] Questions:",
            len(questions)
        )


        # ====================================================
        # UNIQUE PDF NAME
        # ====================================================

        unique_id = (
            uuid.uuid4().hex[:8]
        )


        filename = (
            f"question_paper_{unique_id}.pdf"
        )


        pdf_path = os.path.join(
            app.config["PDF_FOLDER"],
            filename
        )


        print(
            "[2] PDF path:",
            pdf_path
        )


        # ====================================================
        # GENERATE PDF
        # ====================================================

        print(
            "[3] Creating PDF using ReportLab..."
        )


        generate_question_paper_pdf(
            paper_data,
            pdf_path
        )


        # ====================================================
        # VERIFY PDF
        # ====================================================

        if not os.path.exists(
            pdf_path
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "PDF file could not be created."

            }), 500


        pdf_size = os.path.getsize(
            pdf_path
        )


        if pdf_size <= 0:

            return jsonify({

                "success":
                    False,

                "error":
                    "Generated PDF is empty."

            }), 500


        print(
            "[4] PDF created successfully."
        )


        print(
            "[4] PDF size:",
            pdf_size,
            "bytes"
        )


        print()

        print(
            "========================================"
        )

        print(
            "PDF GENERATION COMPLETED"
        )

        print(
            "========================================"
        )


        # ====================================================
        # DOWNLOAD
        # ====================================================

        return send_file(

            pdf_path,

            as_attachment=True,

            download_name=filename,

            mimetype="application/pdf"

        )


    except Exception as error:

        print()

        print(
            "========================================"
        )

        print(
            "PDF GENERATION ERROR"
        )

        print(
            "========================================"
        )


        print(
            "Error Type:",
            type(error).__name__
        )


        print(
            "Error:",
            str(error)
        )


        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success":
            True,

        "application":
            "Smart Q Gen",

        "status":
            "running"

    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "========================================"
    )

    print(
        "SMART Q GEN"
    )

    print(
        "AI QUESTION PAPER GENERATOR"
    )

    print(
        "========================================"
    )

    print(
        "Login: http://localhost:5001/login"
    )

    print(
        "Register: http://localhost:5001/register"
    )

    print(
        "Dashboard: http://localhost:5001/dashboard"
    )

    print(
        "Result: http://localhost:5001/result"
    )

    print(
        "Health: http://localhost:5001/health"
    )

    print(
        "CSS: http://localhost:5001/static/css/style.css"
    )

    print(
        "========================================"
    )


    app.run(
        debug=True,
        port=5001
    )