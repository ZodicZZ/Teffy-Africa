
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getDatabase, ref, set } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";
const firebaseConfig = {
    apiKey: "AIzaSyC_Bafxrtzdw2D3BoXCNGC4XjjyWdurnaM",
    authDomain: "tchat-af17d.firebaseapp.com",
    databaseURL: "https://tchat-af17d-default-rtdb.firebaseio.com",
    projectId: "tchat-af17d",
    storageBucket: "tchat-af17d.appspot.com",
    messagingSenderId: "895463164536",
    appId: "1:895463164536:web:c1cbfc8658ea352b373b8d"
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const database = getDatabase(app);
window.auth = auth;
window.createUserWithEmailAndPassword = createUserWithEmailAndPassword;
window.database = database;
window.ref = ref;
window.set = set;
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('.eye-icon');

    if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                `;
    } else {
        input.type = 'password';
        icon.innerHTML = `
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                `;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("signupForm");
    const inputs = {
        name: {
            input: document.getElementById("name"),
            error: document.getElementById("nameError"),
            status: document.getElementById("nameStatus"),
            validate: (value) => value.length >= 2 && /^[a-zA-Z\s]*$/.test(value),
        },
        email: {
            input: document.getElementById("email"),
            error: document.getElementById("emailError"),
            status: document.getElementById("emailStatus"),
            validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        },
        username: {
            input: document.getElementById("username"),
            error: document.getElementById("usernameError"),
            status: document.getElementById("usernameStatus"),
            validate: (value) => value.length >= 3,
        },
        phone: {
            input: document.getElementById("phone"),
            error: document.getElementById("phoneError"),
            status: document.getElementById("phoneStatus"),
            validate: (value) => /^\+?[\d\s-]{10,}$/.test(value.replace(/[\s-]/g, "")),
        },
        password: {
            input: document.getElementById("password"),
            error: document.getElementById("passwordError"),
            status: document.getElementById("passwordStatus"),
            validate: (value) => value.length >= 8 && /[0-9]/.test(value) && /[a-zA-Z]/.test(value),
        },
        confirmPassword: {
            input: document.getElementById("confirmPassword"),
            error: document.getElementById("confirmPasswordError"),
            status: document.getElementById("confirmPasswordStatus"),
            validate: (value) => value === document.getElementById("password").value && value.length > 0,
        },
        userType: {
            input: document.querySelector('input[name="userType"]'),
            error: document.getElementById("userTypeError"),
            status: document.getElementById("userTypeStatus"),
            validate: () => document.querySelector('input[name="userType"]:checked') !== null,
        }
    };

    const validateField = (field, value) => {
        const isValid = inputs[field].validate(value);
        const input = inputs[field].input;
        const error = inputs[field].error;
        const status = inputs[field].status;

        if (isValid) {
            if (input.classList) input.classList.remove("error");
            if (input.classList) input.classList.add("valid");
            error.style.display = "none";
            status.classList.add("valid");
        } else {
            if (input.classList) input.classList.add("error");
            if (input.classList) input.classList.remove("valid");
            error.style.display = "block";
            status.classList.remove("valid");
        }

        if (field === 'password') {
            validateField('confirmPassword', inputs.confirmPassword.input.value);
        }

        return isValid;
    };

    // Real-time validation
    Object.keys(inputs).forEach((field) => {
        const input = inputs[field].input;
        if (field === 'userType') {
            document.querySelectorAll('input[name="userType"]').forEach(radio => {
                radio.addEventListener("change", () => {
                    validateField(field);
                });
            });
        } else {
            input.addEventListener("input", () => {
                validateField(field, input.value);
            });
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        let isValid = true;

        Object.keys(inputs).forEach((field) => {
            const value = field === 'userType' ? null : inputs[field].input.value;
            if (!validateField(field, value)) {
                isValid = false;
            }
        });

        if (isValid) {
            const name = inputs.name.input.value;
            const email = inputs.email.input.value;
            const password = inputs.password.input.value;
            const username = inputs.username.input.value;
            const phone = inputs.phone.input.value;
            const userType = document.querySelector('input[name="userType"]:checked').value;

            try {
                const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                const userId = userCredential.user.uid;
                await set(ref(database, 'users/' + userId), {
                    name: name,
                    username: username,
                    email: email,
                    phone: phone,
                    bio: "",
                    role: userType
                });
                const response = await fetch("/signup", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ uid: userId })
                });
            } catch (error) {
                alert("Sign up failed: " + error.message);
            }
        }
    });
    const card = document.querySelector(".glass-card");

    card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const angleX = (y - centerY) / 50;
        const angleY = (centerX - x) / 50;

        card.style.transform = `rotateX(${angleX}deg) rotateY(${angleY}deg)`;
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "rotateX(0) rotateY(0)";
    });
});
