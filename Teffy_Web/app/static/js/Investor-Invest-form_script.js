import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getDatabase, ref, get, set, push } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

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
let currentUserData = null;
onAuthStateChanged(auth, async (user) => {
    if (user) {
        const userRef = ref(database, `users/${user.uid}`);
        const snapshot = await get(userRef);
        if (snapshot.exists()) {
            currentUserData = snapshot.val();
            document.getElementById('investorName').value = currentUserData.name || '';
            document.getElementById('investorEmail').value = currentUserData.email || '';
            document.getElementById('investorPhone').value = currentUserData.phone || '';
        }
    } else {
        x1
        window.location.href = '/login';
    }
});
const getFarmId = async () => {
    try {
        const response = await fetch('/get_farm');
        const data = await response.json();
        if (data.farmId) {
            return data.farmId;
        } else {
            throw new Error('Farm ID not found');
        }
    } catch (error) {
        console.error('Error fetching farm ID:', error);
    }
};
const adaExchangeRate = 0.5;
const investmentAmount = document.getElementById('investmentAmount');
const adaAmount = document.getElementById('adaAmount');
investmentAmount.addEventListener('input', () => {
    const usdAmount = parseFloat(investmentAmount.value) || 0;
    const ada = (usdAmount * adaExchangeRate).toFixed(2);
    adaAmount.textContent = ada;
});
const investmentForm = document.getElementById('investmentForm');
const successMessage = document.getElementById('successMessage');
investmentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentUserData) {;
        return;
    }
    const amount = parseFloat(document.getElementById('investmentAmount').value);
    const duration = document.getElementById('duration').value;
    const message = document.getElementById('message').value;
    const timestamp = new Date().toISOString();
    const farmId = await getFarmId();
    if (!farmId) {
        alert('Farm ID not available.');
        return;
    }
    const investmentData = {
        farmId,
        amount,
        duration,
        message,
        timestamp,
        status: 'pending',
        email: currentUserData.email,
        phone: document.getElementById('investorPhone').value
    };
    try {
        const investorName = currentUserData.name.replace(/\s+/g, "_").toLowerCase();
        const investmentRef = ref(database, `investment/${farmId}/${investorName}`);
        const newInvestmentRef = push(investmentRef);
        await set(newInvestmentRef, investmentData);
        successMessage.style.display = 'block';
        investmentForm.reset();
        adaAmount.textContent = "0";
    } catch (error) {
        console.error('Error saving investment:', error);
    }
});
 