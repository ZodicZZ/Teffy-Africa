import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getDatabase, ref, onValue, get } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

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
const database = getDatabase(app);
const notificationsContainer = document.getElementById('notificationsContainer');
async function fetchNotifications() {
    try {
        const response = await fetch("/User_fetch_request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ someKey: "someValue" })
        });
        const data = await response.json();
        const userId = data.user_id;
        if (!userId) {
            showEmptyState("Please log in to view notifications");
            return;
        }

        const landsRef = ref(database, `users/${userId}/land`);
        const landsSnapshot = await get(landsRef);
        if (!landsSnapshot.exists()) {
            showEmptyState("You have no farms registered");
            return;
        }

        const lands = landsSnapshot.val();
        const userFarmIds = Object.keys(lands);
        const investmentsRef = ref(database, 'investments');
        onValue(investmentsRef, (snapshot) => {
            const investments = [];
            if (snapshot.exists()) {
                snapshot.forEach((childSnapshot) => {
                    const investment = childSnapshot.val();
                    if (userFarmIds.includes(investment.farmId)) {
                        investments.push({
                            id: childSnapshot.key,
                            ...investment
                        });
                    }
                });
            }
            if (investments.length === 0) {
                showEmptyState();
            } else {
                displayNotifications(investments);
            }
        }, (error) => {
            console.error("Error fetching investments:", error);
            showError();
        });

    } catch (error) {
        console.error("Error fetching data:", error);
        showError();
    }
}
function displayNotifications(investments) {
    notificationsContainer.innerHTML = investments.map(investment => `
                <div class="notification-card">
                    <div class="notification-header">
                        <div class="investor-info">
                            <div class="investor-avatar">${getInitials(investment.investorName)}</div>
                            <div>
                                <div class="investor-name">${investment.investorName}</div>
                                <div class="notification-time">${formatTime(investment.timestamp)}</div>
                            </div>
                        </div>
                    </div>
                    <div class="notification-content">
                        New investment offer received
                    </div>
                    <div class="investment-details">
                        <div class="detail-row">
                            <span class="detail-label">Investment Amount</span>
                            <span class="detail-value">$${investment.amount.toLocaleString()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Investment Type</span>
                            <span class="detail-value">${investment.type}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">${investment.status}</span>
                        </div>
                    </div>
                    <div class="action-buttons">
                        <button class="action-button accept-button" onclick="acceptInvestment('${investment.id}')">
                            Accept Offer
                        </button>
                        <button class="action-button view-button" onclick="viewInvestmentDetails('${investment.id}')">
                            View Details
                        </button>
                    </div>
                </div>
            `).join('');
}

function showEmptyState(message = "No new notifications") {
    notificationsContainer.innerHTML = `
                <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <h3 class="empty-text">${message}</h3>
                    <p class="empty-subtext">New investment offers will appear here</p>
                </div>
            `;
}

function showError() {
    notificationsContainer.innerHTML = `
                <div class="empty-state">
                    <h3 class="empty-text">Error loading notifications</h3>
                    <p class="empty-subtext">Please try again later</p>
                </div>
            `;
}

function getInitials(name) {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase();
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

fetchNotifications();

window.acceptInvestment = async (investmentId) => {
    try {
        console.log('Accepting investment:', investmentId);
    } catch (error) {
        console.error('Error accepting investment:', error);
    }
};

window.viewInvestmentDetails = (investmentId) => {
    window.location.href = `/investment/${investmentId}`;
};

