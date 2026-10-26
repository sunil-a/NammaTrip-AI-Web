document.addEventListener("DOMContentLoaded", function () {
    // Smoothly scroll to sections when a same-page anchor is clicked.
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener("click", function (event) {
            const targetId = this.getAttribute("href");

            if (targetId && targetId.length > 1) {
                const target = document.querySelector(targetId);

                if (target) {
                    event.preventDefault();

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }
        });
    });

    // Show a useful message when a destination image fails to load.
    document.querySelectorAll(".destination-card img, .result-destination img")
        .forEach(function (img) {
            img.addEventListener("error", function () {
                this.style.display = "none";
            });
        });
});
