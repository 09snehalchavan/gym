// =====================================
// Navbar Scroll Effect
// =====================================

window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".navbar");

    if (window.scrollY > 80) {

        navbar.classList.add("scrolled");

    } else {

        navbar.classList.remove("scrolled");

    }

});


// =====================================
// Counter Animation
// =====================================

const counters = document.querySelectorAll(".counter");

const speed = 80;

function startCounter() {

    counters.forEach(counter => {

        const target = +counter.getAttribute("data-target");

        const update = () => {

            const current = +counter.innerText;

            const increment = Math.ceil(target / speed);

            if (current < target) {

                counter.innerText = current + increment;

                setTimeout(update, 25);

            } else {

                counter.innerText = target;

            }

        };

        update();

    });

}

const counterSection = document.querySelector(".counter-section");

if (counterSection) {

    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                startCounter();

                observer.disconnect();

            }

        });

    });

    observer.observe(counterSection);

}


// =====================================
// Scroll Reveal Animation
// =====================================

const revealElements = document.querySelectorAll(

    ".feature-box, .plan-card, .testimonial, .gallery img"

);

function reveal() {

    revealElements.forEach((el) => {

        const windowHeight = window.innerHeight;

        const top = el.getBoundingClientRect().top;

        if (top < windowHeight - 100) {

            el.style.opacity = "1";

            el.style.transform = "translateY(0px)";

        }

    });

}

revealElements.forEach((el) => {

    el.style.opacity = "0";

    el.style.transform = "translateY(60px)";

    el.style.transition = ".7s ease";

});

window.addEventListener("scroll", reveal);
window.addEventListener("load", reveal);


// =====================================
// Hero Button Hover Effect
// =====================================

document.querySelectorAll(".hero-btn").forEach(btn => {

    btn.addEventListener("mouseenter", () => {

        btn.style.transform = "scale(1.05)";

    });

    btn.addEventListener("mouseleave", () => {

        btn.style.transform = "scale(1)";

    });

});


// =====================================
// Smooth Scroll
// =====================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));

        if (target) {

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});


// =====================================
// Hero Fade Animation
// =====================================

window.addEventListener("load", () => {

    const hero = document.querySelector(".hero");

    if (hero) {

        hero.style.opacity = "0";

        hero.style.transition = "1s";

        setTimeout(() => {

            hero.style.opacity = "1";

        }, 300);

    }

});

// New Script

document.getElementById("markAttendance").addEventListener("click", function (e) {

    e.preventDefault();

    if (navigator.geolocation) {

        navigator.geolocation.getCurrentPosition(function (position) {

            let lat = position.coords.latitude;
            let lng = position.coords.longitude;

            window.location =
                "/mark_attendance?lat=" + lat + "&lng=" + lng;

        });

    } else {

        alert("Location not supported.");

    }

});
