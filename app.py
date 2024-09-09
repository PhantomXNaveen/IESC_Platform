from flask import Flask
from backend.models import *

app = None # Initially None

def init_app():
    app = Flask(__name__) # Object of Flask
    app.debug=True
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///mad1_app.sqlite3"
    app.config['SECRET_KEY'] = "UNKNOWN"
    app.app_context().push()# Direct access app by other modules(db, authentication)
    db.init_app(app) # object.method(<parameter>)
    print("App has Started...")
    create_admin() # Create the admin user 
    return app

# Admin Info
def create_admin():
    username = "admin"
    password = "password"
    
    # with app.app_context():
        # Check if the admin user already exists
    existing_admin = Admin.query.filter_by(user_name=username).first()
    if existing_admin:
        print("Admin user already exists.")
        return
    # Create the admin user
    admin = Admin(user_name=username, password=password)
        
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully.")

app = init_app()
from backend.controllers import *

if __name__=="__main__":
    app.run()



