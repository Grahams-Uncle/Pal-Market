from flask import render_template
from flask_login import current_user
import datetime
from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # render the page by adding information to the index.html file
    return render_template('homepage.html', curuser = current_user)




