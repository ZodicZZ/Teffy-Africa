particlesJS("particles-js", {
        particles: {
          number: {
            value: 30,
            density: {
              enable: true,
              value_area: 800,
            },
          },
          color: {
            value: "#1a8d5f",
          },
          shape: {
            type: "circle",
          },
          opacity: {
            value: 0.1,
            random: true,
          },
          size: {
            value: 3,
            random: true,
          },
          line_linked: {
            enable: false,
          },
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
            onhover: {
              enable: false,
            },
            onclick: {
              enable: false,
            },
            resize: true,
          },
        },
        retina_detect: true,
      });
      import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
      import { getDatabase, ref, get, update } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js";
      import { getAuth } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

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

      particlesJS("particles-js", {
        particles: {
          number: { value: 30, density: { enable: true, value_area: 800 } },
          color: { value: "#1a8d5f" },
          shape: { type: "circle" },
          opacity: { value: 0.1, random: true },
          size: { value: 3, random: true },
          line_linked: { enable: false },
          move: { enable: true, speed: 1, direction: "bottom", random: true, straight: false, out_mode: "out" },
        },
        interactivity: {
          detect_on: "canvas",
          events: { onhover: { enable: false }, onclick: { enable: false }, resize: true },
        },
        retina_detect: true,
      });

      const profileMenuItem = document.getElementById("profileMenuItem");
      const profilePopup = document.getElementById("profilePopup");
      const editProfileBtn = document.getElementById("editProfileBtn");
      const cancelEditBtn = document.getElementById("cancelEditBtn");
      const profileView = document.getElementById("profileView");
      const editProfileSection = document.getElementById("editProfileSection");
      const editProfileForm = document.getElementById("editProfileForm");
      const profilePictureUpload = document.querySelector(".profile-picture-upload");
      const profilePictureInput = document.getElementById("profilePictureInput");

      let isProfileVisible = false;
      profileMenuItem.addEventListener("click", (e) => {
        e.stopPropagation();
        isProfileVisible = !isProfileVisible;
        profilePopup.classList.toggle("active", isProfileVisible);
      });

      document.addEventListener("click", (e) => {
        if (isProfileVisible && !profilePopup.contains(e.target) && !profileMenuItem.contains(e.target)) {
          isProfileVisible = false;
          profilePopup.classList.remove("active");
        }
      });
      editProfileBtn.addEventListener("click", () => {
        profileView.style.display = "none";
        editProfileSection.classList.add("active");
      });

      cancelEditBtn.addEventListener("click", () => {
        profileView.style.display = "block";
        editProfileSection.classList.remove("active");
      });

      profilePictureUpload.addEventListener("click", () => {
        profilePictureInput.click();
      });

      profilePictureInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
          const reader = new FileReader();
          reader.onload = (e) => {
            document.getElementById("editProfileImage").src = e.target.result;
          };
          reader.readAsDataURL(e.target.files[0]);
        }
      });

      async function fetchUserData() {
        try {
          const response = await fetch("/User_fetch_request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ someKey: "someValue" })
          });

          const raw_uid = await response.json();
          if (raw_uid && raw_uid.user_id) {
            const uid = raw_uid.user_id;
            const userRef = ref(database, "users/" + uid);
            const snapshot = await get(userRef);

            if (snapshot.exists()) {
              const data = snapshot.val();
              document.getElementById("profileName").textContent = data.name || "No name available";
              document.getElementById("profileUsername").textContent = data.username || "No username available";
              document.getElementById("profilePhone").textContent = data.phone || "Phone number not provided";
              document.getElementById("profileBio").textContent = data.bio || "Bio not available";
            } else {
              console.warn("No user data found");
            }
          } else {
            window.location.href = "/login";
          }
        } catch (error) {
          console.error("Error fetching user data:", error);
          window.location.href = "/login";  
        }
      }
      editProfileForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = {
          name: document.getElementById("editName").value,
          username: document.getElementById("editUsername").value,
          phone: document.getElementById("editPhone").value,
          bio: document.getElementById("editBio").value,
        };
        try {
          const user = auth.currentUser;
          if (user) {
            const userRef = ref(database, "users/" + user.uid);
            await update(userRef, formData);
            document.getElementById("profileName").textContent = formData.name;
            document.getElementById("profileUsername").textContent = formData.username;
            document.getElementById("profilePhone").textContent = formData.phone;
            document.getElementById("profileBio").textContent = formData.bio;
            profileView.style.display = "block";
            editProfileSection.classList.remove("active");
          }
        } catch (error) {
          console.error("Error updating profile:", error);
        }
      });

      const menuContainer = document.querySelector(".menu-container");
      let isScrolling = false;
      let startX, scrollLeft;

      menuContainer.addEventListener("mousedown", (e) => {
        isScrolling = true;
        startX = e.pageX - menuContainer.offsetLeft;
        scrollLeft = menuContainer.scrollLeft;
      });

      menuContainer.addEventListener("mouseleave", () => isScrolling = false);
      menuContainer.addEventListener("mouseup", () => isScrolling = false);

      menuContainer.addEventListener("mousemove", (e) => {
        if (!isScrolling) return;
        e.preventDefault();
        const x = e.pageX - menuContainer.offsetLeft;
        const walk = (x - startX) * 2;
        menuContainer.scrollLeft = scrollLeft - walk;
      });

      document.querySelectorAll(".menu-item").forEach((item) => {
        item.addEventListener("click", () => {
          document.querySelectorAll(".menu-item").forEach((i) => i.classList.remove("active"));
          item.classList.add("active");
        });
      });

      fetchUserData();