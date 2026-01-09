from flask import Flask, render_template
from app import config
from app.limiter import limiter




app = Flask(__name__)
app.config.from_object('app.config.settings')

limiter.init_app(app)

from app.routes.index import main_bp
from app.routes.errors import errors_bp
from app.routes.admin import admin_bp
from app.routes.loding import loading_bp
from app.routes.register import register_bp

#blueprint
app.register_blueprint(loading_bp)
app.register_blueprint(admin_bp)

app.register_blueprint(errors_bp)
app.register_blueprint(main_bp)
app.register_blueprint(register_bp)




    
