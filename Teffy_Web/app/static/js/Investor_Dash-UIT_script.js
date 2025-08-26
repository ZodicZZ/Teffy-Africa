import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getDatabase, ref, get } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

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

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function updateGalleryDots(currentIndex, totalImages) {
    const galleryNav = document.getElementById('galleryNav');
    galleryNav.innerHTML = '';

    for (let i = 0; i < totalImages; i++) {
        const dot = document.createElement('div');
        dot.className = `gallery-dot ${i === currentIndex ? 'active' : ''}`;
        dot.onclick = () => scrollToImage(i);
        galleryNav.appendChild(dot);
    }
}


function scrollToImage(index) {
    const galleryScroll = document.getElementById('galleryScroll');
    const imageWidth = galleryScroll.offsetWidth;
    galleryScroll.scrollTo({
        left: index * imageWidth,
        behavior: 'smooth'
    });
}

function handleGalleryScroll() {
    const galleryScroll = document.getElementById('galleryScroll');
    const imageWidth = galleryScroll.offsetWidth;
    const currentIndex = Math.round(galleryScroll.scrollLeft / imageWidth);
    const totalImages = galleryScroll.children.length;
    updateGalleryDots(currentIndex, totalImages);
}
document.addEventListener('DOMContentLoaded', async () => {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const galleryScroll = document.getElementById('galleryScroll');

    try {
        const response = await fetch('/get_farm');
        if (!response.ok) throw new Error('Failed to fetch selected farm ID');
        const data = await response.json();
        const farmId = data.farmId;
        console.log('Farm ID:', farmId);
        if (!farmId) throw new Error('No farm ID found');
        const farmRef = ref(database, `farms/${farmId}`);
        const snapshot = await get(farmRef);
        if (snapshot.exists()) {
            const farmData = snapshot.val();
            console.log(farmData);
            if (farmData.images && farmData.images.length > 0) {
                galleryScroll.innerHTML = farmData.images.map(imageUrl => `
                            <img src="${imageUrl}" alt="Farm image" class="gallery-image">
                        `).join('');
                updateGalleryDots(0, farmData.images.length);
                galleryScroll.addEventListener('scroll', handleGalleryScroll);
            } else {
                // Fallback if no images are found
                galleryScroll.innerHTML = `
                            <div class="no-images-placeholder">
                                <p>No images available for this farm.</p>
                            </div>
                        `;
            }

            if (farmData.images && farmData.images.length > 0) {
                galleryScroll.innerHTML = farmData.images.map(imageUrl => `
                            <img src="${imageUrl}" alt="Farm image" class="gallery-image">
                        `).join('');

                updateGalleryDots(0, farmData.images.length);
                galleryScroll.addEventListener('scroll', handleGalleryScroll);
            }
            document.getElementById('farmName').textContent = farmData.farmName || 'Unnamed Farm';
            document.getElementById('farmLocation').innerHTML = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        ${farmData.farmAddress || 'Location not specified'}
                    `;

            document.getElementById('totalArea').textContent = farmData.totalArea ? `${farmData.totalArea}` : '-';
            document.getElementById('fundAmount').textContent = farmData.fundAmount ?
                formatCurrency(farmData.fundAmount) : '-';
            document.getElementById('returnRate').textContent = farmData.returnRate ?
                `${farmData.returnRate}%` : '-';
            document.getElementById('paybackPeriod').textContent = farmData.paybackPeriod || '-';
            const fields = [
                'farmType', 'farmingPractice', 'soilType', 'waterSource', 'certifications',
                'currentRevenue', 'fundingPurpose', 'collateral',
                'ownerName', 'contactEmail', 'contactPhone', 'region'
            ];

            fields.forEach(field => {
                const element = document.getElementById(field);
                if (element) {
                    element.textContent = farmData[field] || 'Not specified';
                }
            });

            document.getElementById('investButton').addEventListener('click', () => {
                window.location.href = `/invest_investor`;
            });
        }
    } catch (error) {
        console.error('Error loading farm details:', error);
    } finally {
        loadingOverlay.style.display = 'none';
    }
});
