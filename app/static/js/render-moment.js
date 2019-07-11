'use strict';
function render_all_timestamps() {
    document.querySelectorAll(".post-date").forEach(function(el) {
        var date = new Date(el.getAttribute("datetime"));
        el.textContent = date.toLocaleDateString("en-GB", {day: "numeric", month: "long", year: "numeric"});
    });
}
document.addEventListener("DOMContentLoaded", render_all_timestamps);
