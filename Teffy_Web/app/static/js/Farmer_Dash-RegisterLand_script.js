
const script = document.createElement('script');
script.src = "https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js";
script.onload = () => {
particlesJS("particles-js", {
    particles: {
    number: { value: 30, density: { enable: true, value_area: 800 } },
    color: { value: "#1a8d5f" },
    shape: { type: "circle" },
    opacity: { value: 0.1, random: true },
    size: { value: 3, random: true },
    line_linked: { enable: false },
    move: {
        enable: true,
        speed: 1,
        direction: "bottom",
        random: true,
        straight: false,
        out_mode: "out",
    },
    },
    interactivity: { detect_on: "canvas", events: { resize: true } },
    retina_detect: true,
});
};
document.head.appendChild(script);

let currentSection = 1;
const totalSections = 5;
const form = document.getElementById("farmRegistrationForm");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");
const submitBtn = document.getElementById("submitBtn");

function showSection(sectionNumber) {
document.querySelectorAll(".form-card").forEach((section) => {
    section.style.display = "none";
});
document.getElementById(`section${sectionNumber}`).style.display = "block";
document.querySelectorAll(".step").forEach((step, index) => {
    if (index + 1 <= sectionNumber) {
    step.classList.add("active");
    } else {
    step.classList.remove("active");
    }
});
prevBtn.style.display = sectionNumber === 1 ? "none" : "block";
nextBtn.style.display = sectionNumber === totalSections ? "none" : "block";
submitBtn.style.display = sectionNumber === totalSections ? "block" : "none";
}

nextBtn.addEventListener("click", () => {
if (currentSection < totalSections) {
    currentSection++;
    showSection(currentSection);
}
});

prevBtn.addEventListener("click", () => {
if (currentSection > 1) {
    currentSection--;
    showSection(currentSection);
}
});

function formatCurrency(input) {
let value = input.value.replace(/[^\d.]/g, "");
value = parseFloat(value).toFixed(2);
if (!isNaN(value)) {
    input.value = value;
}
}

document.querySelectorAll(".currency-input").forEach((input) => {
input.addEventListener("blur", () => formatCurrency(input));
});

document
.querySelector('input[name="farmImages"]')
.addEventListener("change", function (e) {
    const preview = document.getElementById("imagePreview");
    preview.innerHTML = "";

    [...e.target.files].forEach((file) => {
    if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = function (e) {
        const img = document.createElement("img");
        img.src = e.target.result;
        preview.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
    });
});

form.addEventListener("submit", async (e) => {
e.preventDefault();
const formData = new FormData(form);

try {
    const response = await fetch("/register_farm_land", {
    method: "POST",
    body: formData,
    });

    if (response.ok) {
    window.location.href = "/farmer-dashboard";
    } else {
    throw new Error("Registration failed");
    }
} catch (error) {
}
});

showSection(1);
