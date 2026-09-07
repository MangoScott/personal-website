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

// Scroll reveals and count-up numbers, shared by every page
(function () {
    var items = document.querySelectorAll(".reveal");
    if (!items.length) return;

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduceMotion || !("IntersectionObserver" in window)) {
        for (var i = 0; i < items.length; i++) items[i].classList.add("is-visible");
        return;
    }

    // Numbers count up the first time their block scrolls into view
    function countUp(el) {
        var target = parseInt(el.getAttribute("data-count"), 10);
        var suffix = el.getAttribute("data-suffix") || "";
        var start = null;
        var duration = 900;
        function tick(now) {
            if (start === null) start = now;
            var t = Math.min(1, (now - start) / duration);
            var eased = 1 - Math.pow(1 - t, 3);
            el.textContent = Math.round(target * eased) + suffix;
            if (t < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            var numbers = entry.target.querySelectorAll("[data-count]");
            for (var j = 0; j < numbers.length; j++) countUp(numbers[j]);
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });

    for (var k = 0; k < items.length; k++) observer.observe(items[k]);
})();
