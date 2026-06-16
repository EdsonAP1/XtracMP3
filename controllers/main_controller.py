from flask import Blueprint, render_template
import config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', downloads_dir=config.DOWNLOADS_DIR)
