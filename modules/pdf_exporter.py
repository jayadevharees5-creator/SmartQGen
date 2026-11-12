# modules/pdf_exporter.py
# Smart Q Gen
# ============================================================
# QUESTION PAPER PDF EXPORTER
#
# Flow:
#
# Question Paper Data
#        ↓
# Extract Questions
#        ↓
# Format Header
#        ↓
# Format Questions
#        ↓
# Format Options
#        ↓
# ReportLab
#        ↓
# Final Student Question Paper PDF
#
# IMPORTANT:
# - No Unit / Topic / Chapter selection
# - Answers are NOT displayed
# - Source metadata is NOT displayed
# - Internal metadata is NOT displayed
# ============================================================

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


# ============================================================
# PDF QUESTION PAPER GENERATOR
# ============================================================

def generate_question_paper_pdf(
    paper_data,
    output_path
):
    """
    Generate the final student-facing question paper PDF.

    Displayed:
        - Institution
        - Exam title
        - Subject
        - Time allowed
        - Maximum marks
        - Instructions
        - Questions
        - Question marks
        - MCQ / True-False options

    NOT displayed:
        - Answers
        - Concepts
        - Units
        - Topics
        - Chapters
        - Retrieval metadata
        - Source chunks
    """

    # ========================================================
    # CREATE DOCUMENT
    # ========================================================

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    # ========================================================
    # STYLES
    # ========================================================

    institution_style = ParagraphStyle(
        "Institution",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        alignment=TA_CENTER,
        spaceAfter=5
    )

    title_style = ParagraphStyle(
        "ExamTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subject_style = ParagraphStyle(
        "Subject",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    info_style = ParagraphStyle(
        "ExamInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=8
    )

    question_style = ParagraphStyle(
        "Question",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        alignment=TA_LEFT,
        spaceAfter=5
    )

    option_style = ParagraphStyle(
        "Option",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )

    instruction_style = ParagraphStyle(
        "Instructions",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        alignment=TA_LEFT
    )

    story = []

    # ========================================================
    # EXAM INFORMATION
    # ========================================================

    institution = paper_data.get(
        "institution",
        "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING"
    )

    subject = paper_data.get(
        "subject",
        "QUESTION PAPER"
    )

    exam_title = paper_data.get(
        "exam_title",
        "END SEMESTER EXAMINATION"
    )

    time_allowed = paper_data.get(
        "time_allowed",
        "-"
    )

    maximum_marks = paper_data.get(
        "max_marks",
        "-"
    )

    # ========================================================
    # HEADER
    # ========================================================

    story.append(
        Paragraph(
            escape_text(institution),
            institution_style
        )
    )

    story.append(
        Paragraph(
            escape_text(exam_title),
            title_style
        )
    )

    story.append(
        Paragraph(
            escape_text(subject),
            subject_style
        )
    )

    # ========================================================
    # TIME / MAXIMUM MARKS TABLE
    # ========================================================

    info_data = [
        [
            Paragraph(
                f"<b>Time Allowed:</b> "
                f"{escape_text(time_allowed)}",
                info_style
            ),
            Paragraph(
                f"<b>Maximum Marks:</b> "
                f"{escape_text(maximum_marks)}",
                info_style
            )
        ]
    ]

    info_table = Table(
        info_data,
        colWidths=[
            85 * mm,
            85 * mm
        ]
    )

    info_table.setStyle(
        TableStyle([
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.black
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )

    story.append(
        info_table
    )

    story.append(
        Spacer(1, 8)
    )

    # ========================================================
    # GENERAL INSTRUCTIONS
    # ========================================================

    story.append(
        Paragraph(
            "GENERAL INSTRUCTIONS",
            section_style
        )
    )

    instructions = [
        "Answer all questions as instructed.",
        "Read each question carefully before answering.",
        "The questions are generated from the prescribed study material."
    ]

    for instruction in instructions:

        story.append(
            Paragraph(
                f"• {escape_text(instruction)}",
                instruction_style
            )
        )

    story.append(
        Spacer(1, 8)
    )

    # ========================================================
    # GET QUESTIONS
    # ========================================================

    questions = get_questions(
        paper_data
    )

    # ========================================================
    # NO QUESTIONS
    # ========================================================

    if not questions:

        story.append(
            Paragraph(
                "No questions were available.",
                question_style
            )
        )

    # ========================================================
    # QUESTIONS AVAILABLE
    # ========================================================

    else:

        story.append(
            Paragraph(
                "QUESTIONS",
                section_style
            )
        )

        # ====================================================
        # EACH QUESTION
        # ====================================================

        for index, question in enumerate(
            questions,
            start=1
        ):

            # ------------------------------------------------
            # Safety
            # ------------------------------------------------

            if not isinstance(
                question,
                dict
            ):
                continue

            question_elements = []

            # ------------------------------------------------
            # QUESTION TEXT
            # ------------------------------------------------

            question_text = get_question_text(
                question
            )

            # ------------------------------------------------
            # QUESTION MARKS
            # ------------------------------------------------

            marks = get_question_marks(
                question
            )

            # ------------------------------------------------
            # QUESTION TYPE
            # ------------------------------------------------

            question_type = get_question_type(
                question
            )

            # ------------------------------------------------
            # QUESTION NUMBER
            # ------------------------------------------------

            question_number = question.get(
                "question_number",
                index
            )

            # ------------------------------------------------
            # QUESTION HTML
            # ------------------------------------------------

            question_html = (
                f"<b>{escape_text(str(question_number))}. "
                f"{escape_text(question_text)}</b>"
                f" "
                f"<b>[{escape_text(str(marks))} Marks]</b>"
            )

            question_elements.append(
                Paragraph(
                    question_html,
                    question_style
                )
            )

            # =================================================
            # QUESTION OPTIONS
            # =================================================

            options = question.get(
                "options",
                []
            )

            if (
                isinstance(options, list)
                and options
            ):

                # ------------------------------------------------
                # TRUE / FALSE
                # ------------------------------------------------

                if question_type == "TRUE_FALSE":

                    option_elements = [
                        Paragraph(
                            "<b>(A)</b> True",
                            option_style
                        ),
                        Paragraph(
                            "<b>(B)</b> False",
                            option_style
                        )
                    ]

                    option_table = Table(
                        [
                            option_elements
                        ],
                        colWidths=[
                            85 * mm,
                            85 * mm
                        ]
                    )

                    option_table.setStyle(
                        TableStyle([
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP"
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                8
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                3
                            ),
                        ])
                    )

                    question_elements.append(
                        option_table
                    )

                # ------------------------------------------------
                # MCQ / OTHER OPTIONS
                # ------------------------------------------------

                else:

                    option_elements = []

                    option_labels = [
                        "A",
                        "B",
                        "C",
                        "D"
                    ]

                    for option_index, option in enumerate(
                        options
                    ):

                        if option_index >= len(
                            option_labels
                        ):
                            break

                        label = option_labels[
                            option_index
                        ]

                        option_elements.append(
                            Paragraph(
                                (
                                    f"<b>({label})</b> "
                                    f"{escape_text(str(option))}"
                                ),
                                option_style
                            )
                        )

                    # ------------------------------------------------
                    # TWO OPTIONS PER ROW
                    # ------------------------------------------------

                    rows = []

                    for i in range(
                        0,
                        len(option_elements),
                        2
                    ):

                        row = option_elements[
                            i:i + 2
                        ]

                        if len(row) == 1:

                            row.append(
                                ""
                            )

                        rows.append(
                            row
                        )

                    if rows:

                        option_table = Table(
                            rows,
                            colWidths=[
                                85 * mm,
                                85 * mm
                            ]
                        )

                        option_table.setStyle(
                            TableStyle([
                                (
                                    "VALIGN",
                                    (0, 0),
                                    (-1, -1),
                                    "TOP"
                                ),
                                (
                                    "LEFTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    3
                                ),
                                (
                                    "RIGHTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    8
                                ),
                                (
                                    "TOPPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    3
                                ),
                                (
                                    "BOTTOMPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    3
                                ),
                            ])
                        )

                        question_elements.append(
                            option_table
                        )

            # =================================================
            # SPACE AFTER QUESTION
            # =================================================

            question_elements.append(
                Spacer(
                    1,
                    6
                )
            )

            # =================================================
            # ADD QUESTION
            # =================================================

            story.append(
                KeepTogether(
                    question_elements
                )
            )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )


# ============================================================
# PAGE NUMBER
# ============================================================

def add_page_number(
    canvas,
    document
):
    """
    Add page number to the bottom of every page.
    """

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        8
    )

    page_number = canvas.getPageNumber()

    canvas.drawCentredString(
        A4[0] / 2,
        8 * mm,
        f"Page {page_number}"
    )

    canvas.restoreState()


# ============================================================
# GET QUESTIONS
# ============================================================

def get_questions(
    paper_data
):
    """
    Extract questions from supported paper formats.

    Supported:

        {
            "questions": [...]
        }

        {
            "paper": [...]
        }

        {
            "paper": {
                "questions": [...]
            }
        }
    """

    # ========================================================
    # DIRECT LIST
    # ========================================================

    if isinstance(
        paper_data,
        list
    ):

        return paper_data

    # ========================================================
    # INVALID INPUT
    # ========================================================

    if not isinstance(
        paper_data,
        dict
    ):

        return []

    # ========================================================
    # DIRECT QUESTIONS
    # ========================================================

    questions = paper_data.get(
        "questions"
    )

    if isinstance(
        questions,
        list
    ):

        return questions

    # ========================================================
    # PAPER LIST
    # ========================================================

    paper = paper_data.get(
        "paper"
    )

    if isinstance(
        paper,
        list
    ):

        return paper

    # ========================================================
    # NESTED PAPER
    # ========================================================

    if isinstance(
        paper,
        dict
    ):

        nested_questions = paper.get(
            "questions",
            []
        )

        if isinstance(
            nested_questions,
            list
        ):

            return nested_questions

    return []


# ============================================================
# GET QUESTION TEXT
# ============================================================

def get_question_text(
    question
):
    """
    Get question text from supported formats.
    """

    if not isinstance(
        question,
        dict
    ):

        return str(
            question
        )

    return (
        question.get(
            "question"
        )
        or question.get(
            "question_text"
        )
        or question.get(
            "text"
        )
        or question.get(
            "questionText"
        )
        or "Question text unavailable."
    )


# ============================================================
# GET QUESTION TYPE
# ============================================================

def get_question_type(
    question
):
    """
    Get normalized question type.
    """

    if not isinstance(
        question,
        dict
    ):

        return ""

    value = (
        question.get(
            "type"
        )
        or question.get(
            "question_type"
        )
        or ""
    )

    value = str(
        value
    ).strip().upper()

    # Normalize common aliases.

    if value in {
        "MULTIPLE_CHOICE",
        "MULTIPLE CHOICE",
        "MULTIPLE_CHOICE_QUESTION"
    }:

        return "MCQ"

    if value in {
        "TRUE / FALSE",
        "TRUE/FALSE",
        "TRUE OR FALSE"
    }:

        return "TRUE_FALSE"

    if value in {
        "FILL",
        "FILL_BLANK",
        "FILL_BLANKS",
        "FILL_IN_THE_BLANK"
    }:

        return "FILL_IN_THE_BLANKS"

    if value in {
        "SHORT",
        "SHORT ANSWER"
    }:

        return "SHORT_ANSWER"

    if value in {
        "LONG",
        "LONG ANSWER"
    }:

        return "LONG_ANSWER"

    return value


# ============================================================
# GET QUESTION MARKS
# ============================================================

def get_question_marks(
    question
):
    """
    Get marks assigned to a question.

    Priority:

        1. Explicit marks in question
        2. Default based on question type
    """

    if not isinstance(
        question,
        dict
    ):

        return 1

    # ========================================================
    # EXPLICIT MARKS
    # ========================================================

    explicit_marks = question.get(
        "marks"
    )

    if explicit_marks is not None:

        try:

            return int(
                explicit_marks
            )

        except (
            ValueError,
            TypeError
        ):

            try:

                return float(
                    explicit_marks
                )

            except (
                ValueError,
                TypeError
            ):

                pass

    # ========================================================
    # QUESTION TYPE
    # ========================================================

    question_type = get_question_type(
        question
    )

    # ========================================================
    # LONG ANSWER
    # ========================================================

    if question_type == "LONG_ANSWER":

        return 10

    # ========================================================
    # SHORT ANSWER
    # ========================================================

    if question_type == "SHORT_ANSWER":

        return 5

    # ========================================================
    # MCQ
    # ========================================================

    if question_type == "MCQ":

        return 1

    # ========================================================
    # FILL IN THE BLANKS
    # ========================================================

    if question_type == "FILL_IN_THE_BLANKS":

        return 1

    # ========================================================
    # TRUE / FALSE
    # ========================================================

    if question_type == "TRUE_FALSE":

        return 1

    # ========================================================
    # DEFAULT
    # ========================================================

    return 1


# ============================================================
# CALCULATE TOTAL QUESTION MARKS
# ============================================================

def calculate_question_marks(
    questions
):
    """
    Calculate total marks represented by
    the generated questions.

    This is only a fallback calculation.
    If max_marks is already supplied by the
    faculty, that value is displayed instead.
    """

    if not isinstance(
        questions,
        list
    ):

        return 0

    total = 0

    for question in questions:

        total += get_question_marks(
            question
        )

    return total


# ============================================================
# ESCAPE REPORTLAB TEXT
# ============================================================

def escape_text(
    value
):
    """
    Safely escape text before placing it
    inside a ReportLab Paragraph.

    This prevents characters such as:

        &
        <
        >

    from being interpreted as HTML/XML.
    """

    if value is None:

        return ""

    value = str(
        value
    )

    value = value.replace(
        "&",
        "&amp;"
    )

    value = value.replace(
        "<",
        "&lt;"
    )

    value = value.replace(
        ">",
        "&gt;"
    )

    return value