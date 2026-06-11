// Mobile menu toggle, shared by every page
(function () {
    var toggle = document.querySelector(".mobile-menu-toggle");
    var mobileMenu = document.getElementById("mobile-menu");
    var closeBtn = document.getElementById("mobile-menu-close");
    if (!toggle || !mobileMenu || !closeBtn) return;

    var lines = toggle.querySelectorAll(".hamburger-line");
    var links = mobileMenu.querySelectorAll("a");

    function closeMenu() {
        mobileMenu.classList.remove("active");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
        lines[0].style.transform = "none";
        lines[1].style.opacity = "1";
        lines[2].style.transform = "none";
    }

    function openMenu() {
        mobileMenu.classList.add("active");
        toggle.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
        lines[0].style.transform = "rotate(45deg) translate(5px, 5px)";
        lines[1].style.opacity = "0";
        lines[2].style.transform = "rotate(-45deg) translate(5px, -5px)";
    }

    toggle.addEventListener("click", function () {
        if (mobileMenu.classList.contains("active")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    closeBtn.addEventListener("click", closeMenu);

    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", closeMenu);
    }
})();
