"use strict";

document.querySelectorAll(".dialog-dismiss").forEach(el => {
    el.addEventListener("click", evt => {
        evt.preventDefault();
        el.parentNode.removeAttribute("open");
    });
});
