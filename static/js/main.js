// ============================================================
// SMART Q GEN - MAIN JAVASCRIPT
// Faculty Authentication + Dashboard + Question Generation
// ============================================================


// ============================================================
// LOGIN
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const usernameElement =
            document.getElementById("username");

        const passwordElement =
            document.getElementById("password");

        const errorMessage =
            document.getElementById("errorMessage");

        const successMessage =
            document.getElementById("successMessage");

        const loginButton =
            document.getElementById("loginButton");


        const username =
            usernameElement
                ? usernameElement.value.trim()
                : "";

        const password =
            passwordElement
                ? passwordElement.value
                : "";


        // --------------------------------------------------------
        // VALIDATION
        // --------------------------------------------------------

        if (!username || !password) {

            if (errorMessage) {

                errorMessage.textContent =
                    "Please enter your username and password.";

                errorMessage.style.display = "block";
            }

            return;
        }


        // --------------------------------------------------------
        // DISABLE BUTTON
        // --------------------------------------------------------

        if (loginButton) {

            loginButton.disabled = true;
            loginButton.textContent = "Logging in...";
        }


        try {

            const response =
                await fetch("/login", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });


            const result =
                await response.json();


            console.log(
                "[LOGIN] Server response:",
                result
            );


            // ----------------------------------------------------
            // LOGIN FAILED
            // ----------------------------------------------------

            if (!response.ok || !result.success) {

                if (errorMessage) {

                    errorMessage.textContent =
                        result.error ||
                        "Invalid username or password.";

                    errorMessage.style.display =
                        "block";
                }

                if (successMessage) {
                    successMessage.style.display = "none";
                }

                return;
            }


            // ----------------------------------------------------
            // LOGIN SUCCESS
            // ----------------------------------------------------

            if (errorMessage) {
                errorMessage.style.display = "none";
            }


            if (successMessage) {

                successMessage.textContent =
                    "Login successful. Redirecting...";

                successMessage.style.display =
                    "block";
            }


            if (result.username) {

                localStorage.setItem(
                    "facultyUsername",
                    result.username
                );
            }


            if (result.name) {

                localStorage.setItem(
                    "facultyName",
                    result.name
                );
            }


            setTimeout(function () {

                window.location.href =
                    "/dashboard";

            }, 500);


        } catch (error) {

            console.error(
                "[LOGIN] Error:",
                error
            );


            if (errorMessage) {

                errorMessage.textContent =
                    "Unable to connect to the server.";

                errorMessage.style.display =
                    "block";
            }

        } finally {

            if (loginButton) {

                loginButton.disabled =
                    false;

                loginButton.textContent =
                    "Login to System";
            }

        }

    });

}


// ============================================================
// FACULTY REGISTRATION
// ============================================================

const registerForm =
    document.getElementById("registerForm");


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const nameElement =
                document.getElementById("name");

            const usernameElement =
                document.getElementById("username");

            const emailElement =
                document.getElementById("email");

            const passwordElement =
                document.getElementById("password");

            const confirmPasswordElement =
                document.getElementById("confirmPassword");


            const errorMessage =
                document.getElementById("errorMessage");

            const successMessage =
                document.getElementById("successMessage");

            const registerButton =
                document.getElementById("registerButton");


            const name =
                nameElement
                    ? nameElement.value.trim()
                    : "";

            const username =
                usernameElement
                    ? usernameElement.value.trim()
                    : "";

            const email =
                emailElement
                    ? emailElement.value.trim()
                    : "";

            const password =
                passwordElement
                    ? passwordElement.value
                    : "";

            const confirmPassword =
                confirmPasswordElement
                    ? confirmPasswordElement.value
                    : "";


            // ----------------------------------------------------
            // VALIDATION
            // ----------------------------------------------------

            if (
                !name ||
                !username ||
                !email ||
                !password ||
                !confirmPassword
            ) {

                if (errorMessage) {

                    errorMessage.textContent =
                        "Please fill in all fields.";

                    errorMessage.style.display =
                        "block";
                }

                return;
            }


            if (password.length < 6) {

                if (errorMessage) {

                    errorMessage.textContent =
                        "Password must contain at least 6 characters.";

                    errorMessage.style.display =
                        "block";
                }

                return;
            }


            if (password !== confirmPassword) {

                if (errorMessage) {

                    errorMessage.textContent =
                        "Passwords do not match.";

                    errorMessage.style.display =
                        "block";
                }

                return;
            }


            // ----------------------------------------------------
            // DISABLE BUTTON
            // ----------------------------------------------------

            if (registerButton) {

                registerButton.disabled =
                    true;

                registerButton.textContent =
                    "Creating Account...";
            }


            try {

                console.log(
                    "[REGISTER] Creating faculty account..."
                );


                const response =
                    await fetch("/register", {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({

                            name: name,

                            username: username,

                            email: email,

                            password: password,

                            confirmPassword:
                                confirmPassword

                        })
                    });


                const result =
                    await response.json();


                console.log(
                    "[REGISTER] Server response:",
                    result
                );


                // ------------------------------------------------
                // REGISTRATION FAILED
                // ------------------------------------------------

                if (!response.ok || !result.success) {

                    if (errorMessage) {

                        errorMessage.textContent =
                            result.error ||
                            "Registration failed.";

                        errorMessage.style.display =
                            "block";
                    }

                    if (successMessage) {
                        successMessage.style.display =
                            "none";
                    }

                    return;
                }


                // ------------------------------------------------
                // REGISTRATION SUCCESS
                // ------------------------------------------------

                if (errorMessage) {
                    errorMessage.style.display =
                        "none";
                }


                if (successMessage) {

                    successMessage.textContent =
                        "Faculty account created successfully. Redirecting to login...";

                    successMessage.style.display =
                        "block";
                }


                if (passwordElement) {
                    passwordElement.value = "";
                }

                if (confirmPasswordElement) {
                    confirmPasswordElement.value = "";
                }


                setTimeout(function () {

                    window.location.href =
                        "/login";

                }, 1000);


            } catch (error) {

                console.error(
                    "[REGISTER] Error:",
                    error
                );


                if (errorMessage) {

                    errorMessage.textContent =
                        "Unable to connect to the server.";

                    errorMessage.style.display =
                        "block";
                }

            } finally {

                if (registerButton) {

                    registerButton.disabled =
                        false;

                    registerButton.textContent =
                        "Create Faculty Account";
                }

            }

        }
    );

}


// ============================================================
// DASHBOARD ELEMENTS
// ============================================================

const generateForm =
    document.getElementById("generateForm");

const fileInput =
    document.getElementById("pdf_file");

const fileNameDisplay =
    document.getElementById("file-name-display");


// Topic input is kept only for compatibility
// with older dashboard versions.
const topicInput =
    document.getElementById("topic");

const topicStatus =
    document.getElementById("topic-status");


// ============================================================
// FILE SELECTION
// ============================================================

if (fileInput) {

    fileInput.addEventListener(
        "change",
        function () {

            if (this.files.length > 0) {

                const selectedFile =
                    this.files[0];


                if (fileNameDisplay) {

                    fileNameDisplay.textContent =
                        selectedFile.name;
                }


                if (topicStatus) {

                    topicStatus.textContent =
                        "Document selected successfully.";
                }


                if (topicInput) {

                    topicInput.value = "";
                }

            } else {

                if (fileNameDisplay) {

                    fileNameDisplay.textContent =
                        "Click or drag & drop course document here";
                }


                if (topicInput) {

                    topicInput.value = "";
                }


                if (topicStatus) {

                    topicStatus.textContent =
                        "Upload a course document.";
                }

            }

        }
    );

}


// ============================================================
// GENERATION LOADING OVERLAY
// UI ONLY - DOES NOT CHANGE GENERATION LOGIC
// ============================================================

const smartQGenLoadingSteps = [

    [
        "Uploading your document...",
        8
    ],

    [
        "Reading document content...",
        18
    ],

    [
        "Extracting and cleaning text...",
        30
    ],

    [
        "Detecting document structure...",
        42
    ],

    [
        "Building knowledge chunks...",
        54
    ],

    [
        "Searching relevant content...",
        65
    ],

    [
        "Generating questions with AI...",
        76
    ],

    [
        "Validating generated questions...",
        88
    ],

    [
        "Preparing your question paper...",
        96
    ]

];


let smartQGenLoadingTimer = null;

let smartQGenLoadingIndex = 0;


// ============================================================
// SHOW LOADING
// ============================================================

function showSmartQGenLoading() {

    let overlay =
        document.getElementById(
            "smartQGenLoadingOverlay"
        );


    if (!overlay) {

        overlay =
            document.createElement("div");

        overlay.id =
            "smartQGenLoadingOverlay";

        overlay.className =
            "smartqgen-loading-overlay hidden";


        overlay.innerHTML = `

            <div class="smartqgen-loading-card">

                <div class="smartqgen-loading-logo">
                    QG
                </div>

                <div class="smartqgen-loading-spinner"></div>

                <h2>
                    Generating Question Paper
                </h2>

                <p
                    id="smartQGenLoadingStatus"
                    class="smartqgen-loading-status">

                    Preparing your document...

                </p>

                <div class="smartqgen-loading-track">

                    <div
                        id="smartQGenLoadingBar"
                        class="smartqgen-loading-bar">
                    </div>

                </div>

                <div
                    id="smartQGenLoadingPercent"
                    class="smartqgen-loading-percent">

                    0%

                </div>

            </div>

        `;


        document.body.appendChild(
            overlay
        );
    }


    overlay.classList.remove(
        "hidden"
    );


    smartQGenLoadingIndex = 0;


    function updateSmartQGenLoading() {

        const step =
            smartQGenLoadingSteps[
                Math.min(
                    smartQGenLoadingIndex,
                    smartQGenLoadingSteps.length - 1
                )
            ];


        const status =
            document.getElementById(
                "smartQGenLoadingStatus"
            );


        const bar =
            document.getElementById(
                "smartQGenLoadingBar"
            );


        const percent =
            document.getElementById(
                "smartQGenLoadingPercent"
            );


        if (status) {

            status.textContent =
                step[0];
        }


        if (bar) {

            bar.style.width =
                step[1] + "%";
        }


        if (percent) {

            percent.textContent =
                step[1] + "%";
        }


        if (
            smartQGenLoadingIndex <
            smartQGenLoadingSteps.length - 1
        ) {

            smartQGenLoadingIndex++;
        }

    }


    updateSmartQGenLoading();


    if (smartQGenLoadingTimer) {

        clearInterval(
            smartQGenLoadingTimer
        );
    }


    smartQGenLoadingTimer =
        setInterval(
            updateSmartQGenLoading,
            2200
        );

}


// ============================================================
// HIDE LOADING
// ============================================================

function hideSmartQGenLoading() {

    if (smartQGenLoadingTimer) {

        clearInterval(
            smartQGenLoadingTimer
        );

        smartQGenLoadingTimer =
            null;
    }


    const overlay =
        document.getElementById(
            "smartQGenLoadingOverlay"
        );


    if (overlay) {

        overlay.classList.add(
            "hidden"
        );
    }

}


// ============================================================
// GENERATE QUESTION PAPER
// ============================================================

if (generateForm) {

    generateForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const generateButton =
                document.getElementById(
                    "generateButton"
                );


            // ------------------------------------------------
            // CHECK FILE
            // ------------------------------------------------

            if (
                !fileInput ||
                fileInput.files.length === 0
            ) {

                alert(
                    "Please upload a course document first."
                );

                return;
            }


            const file =
                fileInput.files[0];


            // ------------------------------------------------
            // CREATE FORM DATA
            // ------------------------------------------------

            const formData =
                new FormData();


            // IMPORTANT:
            // Flask expects:
            // request.files["file"]
            //
            // Explicitly attach the selected document.

            formData.set(
                "file",
                file,
                file.name
            );


            console.log(
                "[GENERATE] File:",
                file.name
            );


            console.log(
                "[GENERATE] File size:",
                file.size,
                "bytes"
            );


            console.log(
                "[GENERATE] File type:",
                file.type
            );


            console.log(
                "[GENERATE] FormData file:",
                formData.get("file")
            );


            // =================================================
            // SUBJECT
            // =================================================

            const subjectElement =
                document.getElementById(
                    "subject_title"
                );


            if (subjectElement) {

                formData.append(
                    "subject",
                    subjectElement.value.trim()
                );
            }


            // =================================================
            // INSTITUTION
            // =================================================

            const institutionElement =
                document.getElementById(
                    "institution"
                );


            if (institutionElement) {

                formData.append(
                    "institution",
                    institutionElement.value.trim()
                );
            }


            // =================================================
            // MAXIMUM MARKS
            // =================================================

            const marksElement =
                document.getElementById(
                    "max_marks"
                );


            if (marksElement) {

                formData.append(
                    "max_marks",
                    marksElement.value.trim()
                );
            }


            // =================================================
            // TIME ALLOWED
            // =================================================

            const timeElement =
                document.getElementById(
                    "time_allowed"
                );


            if (timeElement) {

                formData.append(
                    "time_allowed",
                    timeElement.value.trim()
                );
            }


            // =================================================
            // NUMBER OF QUESTIONS
            // =================================================

            const numberElement =
                document.getElementById(
                    "num_questions"
                );


            if (numberElement) {

                formData.append(
                    "num_questions",
                    numberElement.value
                );
            }


            // =================================================
            // QUESTION TYPE
            // =================================================

            const questionTypeElement =
                document.getElementById(
                    "question_type"
                );


            if (questionTypeElement) {

                formData.append(
                    "question_type",
                    questionTypeElement.value
                );
            }


            // =================================================
            // DIFFICULTY
            // =================================================

            const difficultyElement =
                document.getElementById(
                    "difficulty"
                );


            if (difficultyElement) {

                formData.append(
                    "difficulty",
                    difficultyElement.value
                );
            }


            // =================================================
            // BLOOM LEVEL
            // =================================================

            const bloomElement =
                document.getElementById(
                    "bloom_level"
                );


            if (bloomElement) {

                formData.append(
                    "bloom_level",
                    bloomElement.value
                );
            }


            // =================================================
            // TOPIC
            // =================================================

            const selectedTopic =
                topicInput
                    ? topicInput.value.trim()
                    : "";


            formData.append(
                "topic",
                selectedTopic
            );


            // =================================================
            // DEBUG INFORMATION
            // =================================================

            console.log(
                "========================================"
            );


            console.log(
                "SMART Q GEN"
            );


            console.log(
                "File:",
                file.name
            );


            console.log(
                "Subject:",
                subjectElement
                    ? subjectElement.value
                    : ""
            );


            console.log(
                "========================================"
            );


            // =================================================
            // DISABLE BUTTON
            // =================================================

            if (generateButton) {

                generateButton.disabled =
                    true;

                generateButton.textContent =
                    "Generating Question Paper...";
            }


            // =================================================
            // SHOW LOADING
            // =================================================

            showSmartQGenLoading();


            // =================================================
            // SEND TO FLASK
            // =================================================

            try {

                console.log(
                    "Sending request to /generate..."
                );


                const response =
                    await fetch(
                        "/generate",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                console.log(
                    "HTTP Status:",
                    response.status
                );


                // ------------------------------------------------
                // READ JSON
                // ------------------------------------------------

                let result;


                try {

                    result =
                        await response.json();

                } catch (jsonError) {

                    throw new Error(
                        "Server returned an invalid response. " +
                        "Check the Flask terminal for the Python error."
                    );

                }


                console.log(
                    "Server response:",
                    result
                );


                // =================================================
                // SERVER ERROR
                // =================================================

                if (
                    !response.ok ||
                    !result.success
                ) {

                    const serverError =
                        result.error ||
                        `Server error (${response.status})`;


                    console.error(
                        "Flask error:",
                        serverError
                    );


                    alert(
                        "Question paper generation failed.\n\n" +
                        serverError
                    );


                    return;
                }


                // =================================================
                // SAVE QUESTION PAPER
                // =================================================

                if (!result.paper) {

                    alert(
                        "The server completed the request, " +
                        "but no question paper was returned."
                    );

                    return;
                }


                sessionStorage.setItem(
                    "questionPaper",
                    JSON.stringify(
                        result.paper
                    )
                );


                sessionStorage.setItem(
                    "selectedTopic",
                    selectedTopic
                );


                // =================================================
                // GO TO RESULT PAGE
                // =================================================

                console.log(
                    "Question paper generated successfully."
                );


                window.location.href =
                    "/result";


            } catch (error) {

                hideSmartQGenLoading();


                console.error(
                    "Generation error:",
                    error
                );


                alert(
                    "Question paper generation failed.\n\n" +
                    error.message
                );


            } finally {

                hideSmartQGenLoading();


                if (generateButton) {

                    generateButton.disabled =
                        false;

                    generateButton.textContent =
                        "⚡ Generate Question Paper";
                }

            }

        }
    );

}


// ============================================================
// DISPLAY FACULTY INFORMATION
// ============================================================

const usernameDisplay =
    document.getElementById(
        "usernameDisplay"
    );


const facultyUsername =
    localStorage.getItem(
        "facultyUsername"
    );


if (
    usernameDisplay &&
    facultyUsername
) {

    usernameDisplay.textContent =
        facultyUsername;
}


// ============================================================
// LOGOUT
// ============================================================

const logoutButton =
    document.getElementById(
        "logoutButton"
    );


if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        async function (event) {

            event.preventDefault();


            try {

                await fetch(
                    "/logout",
                    {
                        method: "POST"
                    }
                );

            } catch (error) {

                console.error(
                    "[LOGOUT] Error:",
                    error
                );

            }


            localStorage.removeItem(
                "facultyUsername"
            );


            localStorage.removeItem(
                "facultyName"
            );


            window.location.href =
                "/login";

        }
    );

}


// ============================================================
// BACK TO DASHBOARD
// ============================================================

const backDashboardButton =
    document.getElementById(
        "backToDashboard"
    );


if (backDashboardButton) {

    backDashboardButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            window.location.href =
                "/dashboard";

        }
    );

}


// ============================================================
// SHOW / HIDE INDIVIDUAL ANSWERS
// ============================================================

const answerButtons =
    document.querySelectorAll(
        ".answer-button"
    );


answerButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                const answerBox =
                    this.nextElementSibling;


                if (!answerBox) {
                    return;
                }


                if (
                    answerBox.style.display ===
                    "block"
                ) {

                    answerBox.style.display =
                        "none";

                    this.textContent =
                        "🔑 Show Answer Key";

                } else {

                    answerBox.style.display =
                        "block";

                    this.textContent =
                        "🔒 Hide Answer Key";
                }

            }
        );

    }
);


// ============================================================
// SHOW / HIDE ALL ANSWERS
// ============================================================

const toggleAnswers =
    document.getElementById(
        "btn-toggle-all-answers"
    );


if (toggleAnswers) {

    let answersVisible =
        false;


    toggleAnswers.addEventListener(
        "click",
        function () {

            answersVisible =
                !answersVisible;


            const answerBoxes =
                document.querySelectorAll(
                    ".answer-box"
                );


            const answerButtons =
                document.querySelectorAll(
                    ".answer-button"
                );


            answerBoxes.forEach(
                function (box) {

                    box.style.display =
                        answersVisible
                            ? "block"
                            : "none";

                }
            );


            answerButtons.forEach(
                function (button) {

                    button.textContent =
                        answersVisible
                            ? "🔒 Hide Answer Key"
                            : "🔑 Show Answer Key";

                }
            );


            this.textContent =
                answersVisible
                    ? "🔒 Hide All Answers"
                    : "👁️ Toggle Answer Keys";

        }
    );

}