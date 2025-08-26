
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
interactivity: {
    detect_on: "canvas",
    events: {
    onhover: { enable: false },
    onclick: { enable: false },
    resize: true,
    },
},
retina_detect: true,
});

// Firebase imports and setup
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import {
getDatabase,
ref,
get,
} from "https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

const firebaseConfig = {
apiKey: "AIzaSyC_Bafxrtzdw2D3BoXCNGC4XjjyWdurnaM",
authDomain: "tchat-af17d.firebaseapp.com",
databaseURL: "https://tchat-af17d-default-rtdb.firebaseio.com",
projectId: "tchat-af17d",
storageBucket: "tchat-af17d.appspot.com",
messagingSenderId: "895463164536",
appId: "1:895463164536:web:c1cbfc8658ea352b373b8d",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const database = getDatabase(app);

async function fetchUserLands() {
try {
    const response = await fetch("/User_fetch_request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ someKey: "someValue" }),
    });
    const raw_uid = await response.json();
    console.log("Fetched UID:", raw_uid);
    if (raw_uid && raw_uid.user_id) {
    const uid = raw_uid.user_id;
    const landsRef = ref(database, `users/${uid}/land/`);
    const snapshot = await get(landsRef);
    console.log("Lands snapshot:", snapshot.val());
    const landsContainer = document.querySelector(".lands-container");
    const emptyState = document.querySelector(".empty-state");
    if (snapshot.exists()) {
        const lands = snapshot.val();
        landsContainer.innerHTML = "";
        Object.entries(lands).forEach(([id, land]) => {
        const landCard = createLandCard(land);
        landsContainer.appendChild(landCard);
        });
        emptyState.style.display = "none";
    } else {
        landsContainer.innerHTML = "";
        emptyState.style.display = "block";
    }
    }
} catch (error) {
    console.error("Error fetching lands:", error);
}
}

function createLandCard(land) {
const card = document.createElement("div");
card.className = "land-card";
card.innerHTML = `
    <img src="${land.image || "https://images.unsplash.com/photo-1500382017468-9049fed747ef"}" alt="${land.title}" class="land-image">
    <div class="land-content">
    <h3 class="land-title">${land.farmName}</h3>
    <div class="land-details">
        <div class="detail-item">
        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
        </svg>
        <span>${land.farmAddress}</span>
        </div>
        <div class="detail-item">
        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path>
        </svg>
        <span>${land.totalArea} Hectors</span>
        </div>
        <div class="detail-item">
        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"></path>
        </svg>
        <span>${land.soilType}</span>
        </div>
        <div class="detail-item">
        <svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"></path>
        </svg>
        <span>${land.waterSource}</span>
        </div>
    </div>
    <span class="land-status ${land.verified ? "status-verified" : "status-pending"}">
        ${land.verified ? "Verified" : "Pending Verification"}
    </span>
    <p class="land-description">${land.description}</p>
    <div class="land-footer">
        <span class="land-price">${land.price && !isNaN(land.price) ? land.price.toLocaleString() : "N/A"}</span>
        <button class="view-details" onclick="window.location.href='/land-details/${land.id}'">View Details</button>
    </div>
    </div>
`;
return card;
}

fetchUserLands();

// Menu item click and drag-scroll functionality (from script.js)
document.querySelectorAll('.menu-item').forEach(item => {
item.addEventListener('click', () => {
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    const route = item.getAttribute('data-route');
    window.location.href = route;
});
});

const menuContainer = document.querySelector('.menu-container');
let isScrolling = false;
let startX;
let scrollLeft;

menuContainer.addEventListener('mousedown', (e) => {
isScrolling = true;
startX = e.pageX - menuContainer.offsetLeft;
scrollLeft = menuContainer.scrollLeft;
});

menuContainer.addEventListener('mouseleave', () => {
isScrolling = false;
});

menuContainer.addEventListener('mouseup', () => {
isScrolling = false;
});

menuContainer.addEventListener('mousemove', (e) => {
if (!isScrolling) return;
e.preventDefault();
const x = e.pageX - menuContainer.offsetLeft;
const walk = (x - startX) * 2;
menuContainer.scrollLeft = scrollLeft - walk;
});

