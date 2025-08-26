
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getDatabase,
  ref,
  get,
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";
import {
  getAuth,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

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
const database = getDatabase(app);
const auth = getAuth(app);

function createReportCard(report) {
  const card = document.createElement("div");
  card.className = "report-card";
  card.innerHTML = `
            <div class="report-date">${new Date(report.timestamp).toLocaleDateString()}</div>
            <h3 class="report-title">${report.title}</h3>
            <p class="report-summary">${report.summary}</p>
            <span class="report-status status-${report.status}">${report.status}</span>
        `;
  return card;
}

async function loadReports(userId) {
  const reportsGrid = document.getElementById("reportsGrid");
  const emptyState = document.getElementById("emptyState");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingMessage = document.getElementById("loadingMessage");

  try {
    const reportsRef = ref(database, `users/${userId}/reports`);
    const snapshot = await get(reportsRef);

    if (snapshot.exists()) {
      loadingMessage.textContent = "Preparing your reports...";
      const reports = snapshot.val();
      reportsGrid.innerHTML = "";

      Object.values(reports).forEach((report, index) => {
        const card = createReportCard(report);
        card.style.animationDelay = `${index * 0.1}s`;
        reportsGrid.appendChild(card);
      });

      emptyState.classList.remove("active");
      reportsGrid.style.display = "grid";
    } else {
      loadingMessage.textContent = "No reports found";
      setTimeout(() => {
        emptyState.classList.add("active");
        reportsGrid.style.display = "none";
      }, 1000);
    }

    setTimeout(() => {
      loadingOverlay.style.opacity = "0";
      setTimeout(() => {
        loadingOverlay.style.display = "none";
      }, 500);
    }, 1500);
  } catch (error) {
    console.error("Error loading reports:", error);
    loadingMessage.textContent = "Unable to load reports";
    setTimeout(() => {
      loadingOverlay.style.display = "none";
    }, 1500);
  }
}

onAuthStateChanged(auth, (user) => {
  if (user) {
    loadReports(user.uid);
  } else {
    window.location.href = "/login";
  }
});
