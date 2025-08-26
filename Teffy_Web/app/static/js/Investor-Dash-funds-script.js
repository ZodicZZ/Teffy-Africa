
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

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

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function updateFundDisplay(funds) {
    const fundStats = document.getElementById('fundStats');
    const noFunds = document.getElementById('noFunds');

    if (funds && Object.keys(funds).length > 0) {
        document.getElementById('totalInvestment').textContent = formatCurrency(funds.totalInvestment || 0);
        document.getElementById('expectedReturn').textContent = formatCurrency(funds.expectedReturn || 0);
        document.getElementById('currentBalance').textContent = formatCurrency(funds.currentBalance || 0);

        fundStats.style.display = 'grid';
        noFunds.style.display = 'none';

        document.querySelectorAll('.stat-box').forEach((box, index) => {
            box.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1}s`;
        });
    } else {
        fundStats.style.display = 'none';
        noFunds.style.display = 'block';
    }
}

onAuthStateChanged(auth, (user) => {
    if (user) {
        const fundsRef = ref(database, `users/${user.uid}/funds`);
        onValue(fundsRef, (snapshot) => {
            const funds = snapshot.val();
            updateFundDisplay(funds);
        });
    } else {
        updateFundDisplay(null);
    }
});
