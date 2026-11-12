// ============================================================
// SMART Q GEN - MAIN JAVASCRIPT
// ============================================================


// ============================================================
// LOGIN
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const usernameInput =
            document.getElementById("username");

        const passwordInput =
            document.getElementById("password");

        const errorMessage =
            document.getElementById("errorMessage");

        const successMessage =
            document.getElementById("successMessage");

        const loginButton =
            document.getElementById("loginButton");


        const username =
            usernameInput
                ? usernameInput.value.trim()
                : "";

        const password =
            passwordInput
                ? passwordInput.value
                : "";


        // --------------------------------------------------------
        // CLEAR PREVIOUS MESSAGES
        // --------------------------------------------------------

        if (errorMessage) {

            errorMessage.style.display = "none";
            errorMessage.textContent = "";

        }

        if (successMessage) {

            successMessage.style.display = "none";
            successMessage.textContent = "";

        }


        // --------------------------------------------------------
        // BASIC VALIDATION
        // --------------------------------------------------------

        if (!username || !password) {

            if (errorMessage) {

                errorMessage.textContent =
                    "Please enter your username and password.";

                errorMessage.style.display =
                    "block";

            }

            return;
        }


        // --------------------------------------------------------
        // DISABLE LOGIN BUTTON
        // --------------------------------------------------------

        if (loginButton) {

            loginButton.disabled = true;

            loginButton.textContent =
                "Logging in...";

        }


        try {

            // ----------------------------------------------------
            // SEND LOGIN REQUEST TO FLASK
            // ----------------------------------------------------

            const response = await fetch(
                "/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                }
            );


            const result =
                await response.json();


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

                return;
            }


            // ----------------------------------------------------
            // STORE USERNAME FOR UI ONLY
            // ----------------------------------------------------
            //
            // Authentication is handled by Flask session.
            // This localStorage value is only used to display
            // the faculty username in the dashboard.
            //

            localStorage.setItem(
                "facultyUsername",
                result.username || username
            );


            // ----------------------------------------------------
            // SHOW SUCCESS MESSAGE
            // ----------------------------------------------------

            if (successMessage) {

                successMessage.textContent =
                    result.message ||
                    "Login successful. Redirecting...";

                successMessage.style.display =
                    "block";

            }


            // ----------------------------------------------------
            // REDIRECT TO DASHBOARD
            // ----------------------------------------------------

            setTimeout(function () {

                window.location.href =
                    "/dashboard";

            }, 700);


        } catch (error) {

            console.error(
                "Login error:",
                error
            );


            if (errorMessage) {

                errorMessage.textContent =
                    "Unable to connect to the Flask server.";

                errorMessage.style.display =
                    "block";

            }


        } finally {

            // ----------------------------------------------------
            // ENABLE LOGIN BUTTON
            // ----------------------------------------------------

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
// REGISTER
// ============================================================

const registerForm =
    document.getElementById("registerForm");


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            // ----------------------------------------------------
            // GET FORM ELEMENTS
            // ----------------------------------------------------

            const nameInput =
                document.getElementById("name");

            const usernameInput =
                document.getElementById("username");

            const emailInput =
                document.getElementById("email");

            const passwordInput =
                document.getElementById("password");

            const confirmPasswordInput =
                document.getElementById("confirmPassword");

            const registerButton =
                document.getElementById("registerButton");

            const errorMessage =
                document.getElementById("errorMessage");

            const successMessage =
                document.getElementById("successMessage");


            // ----------------------------------------------------
            // GET VALUES
            // ----------------------------------------------------

            const name =
                nameInput
                    ? nameInput.value.trim()
                    : "";

            const username =
                usernameInput
                    ? usernameInput.value.trim()
                    : "";

            const email =
                emailInput
                    ? emailInput.value.trim()
                    : "";

            const password =
                passwordInput
                    ? passwordInput.value
                    : "";

            const confirmPassword =
                confirmPasswordInput
                    ? confirmPasswordInput.value
                    : "";


            // ----------------------------------------------------
            // CLEAR PREVIOUS MESSAGES
            // ----------------------------------------------------

            if (errorMessage) {

                errorMessage.style.display =
                    "none";

                errorMessage.textContent =
                    "";

            }

            if (successMessage) {

                successMessage.style.display =
                    "none";

                successMessage.textContent =
                    "";

            }


            // ----------------------------------------------------
            // BASIC VALIDATION
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


            // ----------------------------------------------------
            // USERNAME VALIDATION
            // ----------------------------------------------------

            if (username.length < 3) {

                if (errorMessage) {

                    errorMessage.textContent =
                        "Username must contain at least 3 characters.";

                    errorMessage.style.display =
                        "block";

                }

                return;
            }


            // ----------------------------------------------------
            // PASSWORD LENGTH
            // ----------------------------------------------------

            if (password.length < 6) {

                if (errorMessage) {

                    errorMessage.textContent =
                        "Password must contain at least 6 characters.";

                    errorMessage.style.display =
                        "block";

                }

                return;
            }


            // ----------------------------------------------------
            // CONFIRM PASSWORD
            // ----------------------------------------------------

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
            // DISABLE REGISTER BUTTON
            // ----------------------------------------------------

            if (registerButton) {

                registerButton.disabled =
                    true;

                registerButton.textContent =
                    "Creating Account...";

            }


            try {

                // ------------------------------------------------
                // SEND REGISTRATION REQUEST TO FLASK
                // ------------------------------------------------

                const response = await fetch(
                    "/register",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({

                            name: name,

                            username: username,

                            email: email,

                            password: password,

                            // IMPORTANT:
                            // Flask app.py expects this field.

                            confirmPassword:
                                confirmPassword

                        })
                    }
                );


                const result =
                    await response.json();


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

                    return;
                }


                // ------------------------------------------------
                // REGISTRATION SUCCESSFUL
                // ------------------------------------------------

                if (successMessage) {

                    successMessage.textContent =
                        result.message ||
                        "Registration successful. Redirecting to login...";

                    successMessage.style.display =
                        "block";

                }


                // ------------------------------------------------
                // CLEAR FORM
                // ------------------------------------------------

                registerForm.reset();


                // ------------------------------------------------
                // REDIRECT TO LOGIN
                // ------------------------------------------------

                setTimeout(function () {

                    window.location.href =
                        "/login";

                }, 1200);


            } catch (error) {

                console.error(
                    "Registration error:",
                    error
                );


                if (errorMessage) {

                    errorMessage.textContent =
                        "Unable to connect to the Flask server.";

                    errorMessage.style.display =
                        "block";

                }


            } finally {

                // ------------------------------------------------
                // ENABLE REGISTER BUTTON
                // ------------------------------------------------

                if (registerButton) {

                    registerButton.disabled =
                        false;

                    registerButton.textContent =
                        "Create Account";

                }

            }

        }
    );

}



// ============================================================
// DASHBOARD - GENERATE QUESTION PAPER
// ============================================================

const generateForm =
    document.getElementById("generateForm");


if (generateForm) {

    generateForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const fileInput =
                document.getElementById("pdf_file");

            const generateButton =
                document.getElementById(
                    "generateButton"
                );


            // ----------------------------------------------------
            // CHECK FILE
            // ----------------------------------------------------

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


            // =================================================
            // CREATE FORMDATA
            // =================================================

            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            // ----------------------------------------------------
            // SUBJECT
            // ----------------------------------------------------

            const subjectElement =
                document.getElementById(
                    "subject_title"
                );

            if (subjectElement) {

                formData.append(
                    "subject",
                    subjectElement.value
                );

            }


            // ----------------------------------------------------
            // INSTITUTION
            // ----------------------------------------------------

            const institutionElement =
                document.getElementById(
                    "institution"
                );

            if (institutionElement) {

                formData.append(
                    "institution",
                    institutionElement.value
                );

            }


            // ----------------------------------------------------
            // MAXIMUM MARKS
            // ----------------------------------------------------

            const maxMarksElement =
                document.getElementById(
                    "max_marks"
                );

            if (maxMarksElement) {

                formData.append(
                    "max_marks",
                    maxMarksElement.value
                );

            }


            // ----------------------------------------------------
            // TIME ALLOWED
            // ----------------------------------------------------

            const timeAllowedElement =
                document.getElementById(
                    "time_allowed"
                );

            if (timeAllowedElement) {

                formData.append(
                    "time_allowed",
                    timeAllowedElement.value
                );

            }


            // ----------------------------------------------------
            // NUMBER OF QUESTIONS
            // ----------------------------------------------------

            const numberQuestionsElement =
                document.getElementById(
                    "num_questions"
                );

            if (numberQuestionsElement) {

                formData.append(
                    "num_questions",
                    numberQuestionsElement.value
                );

            }


            // ----------------------------------------------------
            // QUESTION TYPE
            // ----------------------------------------------------

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


            // ----------------------------------------------------
            // DIFFICULTY
            // ----------------------------------------------------

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


            // ----------------------------------------------------
            // BLOOM LEVEL
            // ----------------------------------------------------

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
            // NO UNIT / TOPIC / CHAPTER SELECTION
            // =================================================
            //
            // Units, topics and chapters are detected internally
            // by the backend.
            //
            // We intentionally do NOT send:
            //
            // formData.append("unit", ...)
            // formData.append("topic", ...)
            //
            // =================================================


            console.log(
                "Generating question paper from uploaded document..."
            );


            // =================================================
            // DISABLE GENERATE BUTTON
            // =================================================

            if (generateButton) {

                generateButton.disabled =
                    true;

                generateButton.textContent =
                    "Generating Question Paper...";

            }


            try {

                // =================================================
                // SEND TO FLASK
                // =================================================

                const response =
                    await fetch(
                        "/generate",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const result =
                    await response.json();


                // =================================================
                // SESSION EXPIRED
                // =================================================

                if (response.status === 401) {

                    localStorage.removeItem(
                        "facultyUsername"
                    );

                    alert(
                        "Your login session has expired. Please login again."
                    );

                    window.location.href =
                        "/login";

                    return;
                }


                // =================================================
                // CHECK RESPONSE
                // =================================================

                if (
                    !response.ok ||
                    !result.success
                ) {

                    alert(
                        result.error ||
                        "Question paper generation failed."
                    );

                    return;
                }


                // =================================================
                // STORE GENERATED PAPER
                // =================================================

                sessionStorage.setItem(
                    "questionPaper",
                    JSON.stringify(
                        result.paper
                    )
                );


                // =================================================
                // OPEN RESULT PAGE
                // =================================================

                window.location.href =
                    "/result";


            } catch (error) {

                console.error(
                    "Generation error:",
                    error
                );


                alert(
                    "Unable to connect to the Flask server."
                );


            } finally {

                // =================================================
                // ENABLE BUTTON AGAIN
                // =================================================

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
// SHOW SELECTED FILE NAME
// ============================================================

const fileInput =
    document.getElementById(
        "pdf_file"
    );


const fileNameDisplay =
    document.getElementById(
        "file-name-display"
    );


if (
    fileInput &&
    fileNameDisplay
) {

    fileInput.addEventListener(
        "change",
        function () {

            if (this.files.length > 0) {

                fileNameDisplay.textContent =
                    this.files[0].name;

            } else {

                fileNameDisplay.textContent =
                    "Click or drag & drop course document here";

            }

        }
    );

}



// ============================================================
// DISPLAY FACULTY USERNAME
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


            // ----------------------------------------------------
            // DISABLE BUTTON
            // ----------------------------------------------------

            logoutButton.disabled =
                true;


            try {

                // ------------------------------------------------
                // DESTROY FLASK SESSION
                // ------------------------------------------------

                const response =
                    await fetch(
                        "/logout",
                        {
                            method: "POST"
                        }
                    );


                if (!response.ok) {

                    console.warn(
                        "Logout request returned:",
                        response.status
                    );

                }


            } catch (error) {

                console.error(
                    "Logout error:",
                    error
                );


            } finally {

                // ------------------------------------------------
                // REMOVE UI-ONLY USERNAME
                // ------------------------------------------------

                localStorage.removeItem(
                    "facultyUsername"
                );


                // ------------------------------------------------
                // CLEAR GENERATED PAPER
                // ------------------------------------------------

                sessionStorage.removeItem(
                    "questionPaper"
                );


                // ------------------------------------------------
                // REDIRECT TO LOGIN
                // ------------------------------------------------

                window.location.href =
                    "/login";

            }

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