'use strict';
moment.locale("en_GB");

function flask_moment_render(el) {
    el.textContent = eval('moment("' + el.getAttribute('data-timestamp') + '").' + el.getAttribute('data-format') + ';');
    el.classList.remove('flask-moment');
    el.style.display = '';
}

function flask_moment_render_all() {
    document.querySelectorAll('.flask-moment').forEach(function(el) {
        flask_moment_render(el);
        if (el.getAttribute('data-refresh')) {
            (function(el, interval) {
                setInterval(function() {
                    flask_moment_render(el);
                }, interval);
            })(el, el.getAttribute('data-refresh'));
        }
    });
}
document.addEventListener("DOMContentLoaded", flask_moment_render_all);
