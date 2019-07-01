from flask import jsonify, render_template, request

from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    if (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html):
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template('404.html.j2'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html):
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template('500.html.j2'), 500
