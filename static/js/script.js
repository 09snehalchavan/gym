/*=========================================
        Gym Management System
        Professional JavaScript
=========================================*/

document.addEventListener("DOMContentLoaded", function () {

    /*==============================
        Sticky Navbar
    ==============================*/

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", function () {

        if (window.scrollY > 50) {

            navbar.classList.add("scrolled");

        } else {

            navbar.classList.remove("scrolled");

        }

    });


    /*==============================
        Scroll Reveal
    ==============================*/

    const reveals = document.querySelectorAll(".reveal");

    function revealElements() {

        const windowHeight = window.innerHeight;

        reveals.forEach(function (element) {

            const elementTop = element.getBoundingClientRect().top;

            if (elementTop < windowHeight - 100) {

                element.classList.add("active");

            }

        });

    }

    window.addEventListener("scroll", revealElements);

    revealElements();


    /*==============================
        Counter Animation
    ==============================*/

    const counters = document.querySelectorAll(".counter");

    counters.forEach(counter => {

        counter.innerText = "0";

        const updateCounter = () => {

            const target = +counter.getAttribute("data-target");

            const count = +counter.innerText;

            const increment = target / 150;

            if (count < target) {

                counter.innerText = Math.ceil(count + increment);

                setTimeout(updateCounter, 15);

            } else {

                counter.innerText = target;

            }

        };

        updateCounter();

    });


    /*==============================
        Auto Close Mobile Navbar
    ==============================*/

    const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

    const navbarCollapse = document.querySelector(".navbar-collapse");

    navLinks.forEach(link => {

        link.addEventListener("click", () => {

            if (navbarCollapse.classList.contains("show")) {

                new bootstrap.Collapse(navbarCollapse).hide();

            }

        });

    });


    /*==============================
        Smooth Scroll
    ==============================*/

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


    /*==============================
        Active Navbar Link
    ==============================*/

    const sections = document.querySelectorAll("section");

    const navItems = document.querySelectorAll(".nav-link");

    window.addEventListener("scroll", () => {

        let current = "";

        sections.forEach(section => {

            const sectionTop = section.offsetTop - 150;

            if (pageYOffset >= sectionTop) {

                current = section.getAttribute("id");

            }

        });

        navItems.forEach(link => {

            link.classList.remove("active");

            if (link.getAttribute("href") == "#" + current) {

                link.classList.add("active");

            }

        });

    });


    /*==============================
        Back To Top Button
    ==============================*/

    const backTop = document.getElementById("backToTop");

    if (backTop) {

        window.addEventListener("scroll", () => {

            if (window.scrollY > 300) {

                backTop.style.display = "flex";

            } else {

                backTop.style.display = "none";

            }

        });

        backTop.addEventListener("click", () => {

            window.scrollTo({

                top: 0,

                behavior: "smooth"

            });

        });

    }


    /*==============================
        Loading Screen
    ==============================*/

    const loader = document.getElementById("loader");

    if (loader) {

        window.addEventListener("load", () => {

            loader.style.opacity = "0";

            setTimeout(() => {

                loader.style.display = "none";

            }, 500);

        });

    }

});


/*=========================================
        AOS Animation
=========================================*/

AOS.init({

    duration: 1000,

    once: true,

    easing: "ease-in-out"

});