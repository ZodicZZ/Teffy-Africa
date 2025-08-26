
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
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
const database = getDatabase(app);

const farmsGrid = document.getElementById('farmsGrid');
const searchInput = document.getElementById('searchInput');
let allFarms = [];

const farmsRef = ref(database, 'farms');
onValue(farmsRef, (snapshot) => {
    farmsGrid.innerHTML = '';
    allFarms = [];

    snapshot.forEach((farmSnapshot) => {
        const farmData = farmSnapshot.val();
        const farmId = farmSnapshot.key;
        allFarms.push({
            id: farmId,
            ...farmData
        });
    });

    displayFarms(allFarms);
}, (error) => {
    console.error("Error fetching farms:", error);
    farmsGrid.innerHTML = '<div class="loading">Error loading farms. Please try again later.</div>';
});

window.sendFarmIdToBackend = function (farmId) {
    fetch('/select_farm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ farmId: farmId })
    }).then(response => {
        if (response.redirected) {
            window.location.href = '/Search_details_farmers';
        }
    }).catch(error => {
        console.error('Error sending farm ID:', error);
    });
};
function displayFarms(farms) {
    farmsGrid.innerHTML = farms.map(farm => `
                <div class="farm-card">
                    <div class="farm-header">
                        <div>
                            <h2 class="farm-name">${farm.farmName || 'Unnamed Farm'}</h2>
                            <div class="farm-location">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                                    <circle cx="12" cy="10" r="3"></circle>
                                </svg>
                                ${farm.farmAddress || 'Location not specified'}
                            </div>
                        </div>
                    </div>
                    <div class="farm-details">
                        <div class="detail-item">
                            <span class="detail-label">Farm Size</span>
                            <span class="detail-value">${farm.totalArea || 'N/A'} acres</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Crops</span>
                            <span class="detail-value">${farm.crops ? farm.crops.join(', ') : 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Investment Needed</span>
                            <span class="detail-value">$${farm.fundAmount?.toLocaleString() || 'N/A'}</span>
                        </div>
                    </div>
                    <button class="invest-button" onclick="sendFarmIdToBackend('${farm.id}')">View Details & Invest</button>
                </div>
            `).join('');
}

searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const filteredFarms = allFarms.filter(farm =>
        (farm.farmName?.toLowerCase().includes(searchTerm)) ||
        (farm.farmAddress?.toLowerCase().includes(searchTerm)) ||
        (farm.crops?.some(crop => crop.toLowerCase().includes(searchTerm)))
    );
    displayFarms(filteredFarms);
});
