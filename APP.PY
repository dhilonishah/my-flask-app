from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "secretpassword"

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'samip'
jwt = JWTManager(app)
app.config['SECRET_KEY'] = 'yoursecretkeyhere'

# Set up the database engine
engine = create_engine('sqlite:///data.db', echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    currently_working = Column(String)
    start_date = Column(String)
    job_title = Column(String)
    name_of_role = Column(String)
    country_of_work = Column(String)
    state_or_region = Column(String)
    country_of_org = Column(String)
    org_name = Column(String)
    org_address = Column(Text)
    org_phone = Column(String)
    org_email = Column(String)

Base.metadata.create_all(bind=engine)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        # Show a login form every time (no session)
        return """
        <h1>Login Required</h1>
        <form method="post">
          <label>Username:</label><input type="text" name="username" required><br><br>
          <label>Password:</label><input type="password" name="password" required><br><br>
          <button type="submit">Login</button>
        </form>
        """

    else:
        # Handle POST - Check credentials each time
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Credentials correct, show form immediately
            with open('index.html', 'r') as f:
                return f.read()
        else:
            # Wrong credentials, show login page again with error
            return """
            <h1>Invalid credentials</h1>
            <p><a href="/">Try again</a></p>
            """

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(msg="Invalid credentials"), 401

@app.route('/submit', methods=['POST'])
def submit():
    db = SessionLocal()
    data = Submission(
        currently_working=request.form.get('currentlyWorking'),
        start_date=request.form.get('startDate'),
        job_title=request.form.get('jobTitle'),
        name_of_role=request.form.get('nameOfRole'),
        country_of_work=request.form.get('countryOfWork'),
        state_or_region=request.form.get('stateOrRegion'),
        country_of_org=request.form.get('countryOfOrg'),
        org_name=request.form.get('orgName'),
        org_address=request.form.get('orgAddress'),
        org_phone=request.form.get('orgPhone'),
        org_email=request.form.get('orgEmail')
    )

    db.add(data)
    db.commit()
    db.close()

    return "<h1>Form Submitted Successfully</h1><p><a href='/'>Go back</a></p>"

@app.route('/admin')
@jwt_required()
def admin():
    db = SessionLocal()
    submissions = db.query(Submission).all()
    db.close()

    data = []
    for sub in submissions:
        data.append({
            "id": sub.id,
            "currently_working": sub.currently_working,
            "start_date": sub.start_date,
            "job_title": sub.job_title,
            "name_of_role": sub.name_of_role,
            "country_of_work": sub.country_of_work,
            "state_or_region": sub.state_or_region,
            "country_of_org": sub.country_of_org,
            "org_name": sub.org_name,
            "org_address": sub.org_address,
            "org_phone": sub.org_phone,
            "org_email": sub.org_email
        })

    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
