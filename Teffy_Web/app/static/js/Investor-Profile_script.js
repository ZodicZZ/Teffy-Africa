
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getDatabase, ref, get, update } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js";
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

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

onAuthStateChanged(auth, async (user) => {
  if (user) {
    const uid = user.uid;
    const userRef = ref(database, "users/" + uid);
    const snapshot = await get(userRef);

    if (snapshot.exists()) {
      const data = snapshot.val();
      document.querySelector(".profile-title").textContent = data.name || "No name";
      document.querySelector(".profile-subtitle").textContent = "@" + (data.username || "nouser");
      document.querySelectorAll('.field-value')[0].textContent = data.email || "No email";
      document.querySelectorAll('.field-value')[1].textContent = data.phone || "No phone";
      document.querySelectorAll('.field-value')[2].textContent = data.location || "No location";
      document.querySelectorAll('.field-value')[3].textContent = data.bio || "No bio";

      const initials = data.name?.split(' ').map(n => n[0]).join('').toUpperCase();
      document.getElementById('profileAvatar').textContent = initials || "U";

      document.getElementById('editName').value = data.name || "";
      document.getElementById('editEmail').value = data.email || "";
      document.getElementById('editPhone').value = data.phone || "";
      document.getElementById('editLocation').value = data.location || "";
      document.getElementById('editBio').value = data.bio || "";
    }
  } else {
    window.location.href = "/login";
  }
});
const editForm = document.getElementById('editProfileForm');
const editBtn = document.getElementById('editProfileBtn');
const cancelBtn = document.getElementById('cancelEditBtn');
const profileView = document.getElementById('profileView');

function showEditForm() {
  editForm.classList.add('active');
  profileView.style.display = 'none';
}

function hideEditForm() {
  editForm.classList.remove('active');
  profileView.style.display = 'grid';
}
editBtn.addEventListener('click', showEditForm);
cancelBtn.addEventListener('click', hideEditForm);
editForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const user = auth.currentUser;
  if (!user) return alert("Not authenticated.");
  const uid = user.uid;
  const formData = {
    name: document.getElementById('editName').value,
    email: document.getElementById('editEmail').value,
    phone: document.getElementById('editPhone').value,
    location: document.getElementById('editLocation').value,
    bio: document.getElementById('editBio').value
  };
  try {
    const userRef = ref(database, "users/" + uid);
    await update(userRef, formData);

    document.querySelector(".profile-title").textContent = formData.name;
    document.querySelector(".profile-subtitle").textContent = "@" + (formData.username || "nouser");
    document.querySelectorAll('.field-value')[0].textContent = formData.email;
    document.querySelectorAll('.field-value')[1].textContent = formData.phone;
    document.querySelectorAll('.field-value')[2].textContent = formData.location;
    document.querySelectorAll('.field-value')[3].textContent = formData.bio;

    const initials = formData.name.split(' ').map(n => n[0]).join('').toUpperCase();
    document.getElementById('profileAvatar').textContent = initials;

    hideEditForm();
  } catch (error) {
    console.error("Error updating profile:", error);
  }
});
