// Sidebar Toggle

const menuBtn = document.querySelector(".menu-btn");
const sidebar = document.querySelector(".sidebar");
const overlay = document.querySelector(".overlay");

menuBtn.addEventListener("click", () => {

    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");

});

overlay.addEventListener("click", () => {

    sidebar.classList.remove("active");
    overlay.classList.remove("active");

});

// Close sidebar after clicking menu item (Mobile)

document.querySelectorAll(".sidebar .nav-link").forEach(link => {

    link.addEventListener("click", () => {

        if (window.innerWidth <= 991) {

            sidebar.classList.remove("active");
            overlay.classList.remove("active");

        }

    });

});