# comp0034_flask_login
COMP0034 Code to accompany the lecture covering Flask login, sessions and cookies.

You will need to create a venv and install the requirements from requirements.txt.

### Exercise 1: Cookies
1. Create a cookie in the signup route as soon as a new user has been successfully created. The cookie should use the value of the name field from the form to create a cookie called name. 
After creating the cookie, the user should be directed to the home page.

    To set the cookie you need to: 
    - create a response (in this case the response is to redirect to the URL for the home page)
    - set the cookie for the response, the cookie is called `name` and the value for the name is captured in the form.name field.
    - return the response
   e.g. find the correct location in your signup route and add the following (you will also need to add an import `from flask import make_response` to the imports in `routes.py`
    ```python
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie("name", form.name.data)
    return response
    ```
2. Add a new route to delete the cookie, this is just so that we can see the effect on the index page after the cookie is deleted.
    To delete a cookie, you set its expiration as a date in the past.
    ```python
    @bp_main.route('/delete_cookie')
    def delete_cookie():
        response = make_response(redirect(url_for('main.index')))
        response.set_cookie('name', '', expires=datetime.now())
        return response
    ```
3. To see the value of the cookie, let's modify the `index` page to display a welcome message with the name value if a cookie has been set.
To read a cookie, you need to access the request object.
    ```python
    @bp_main.route('/')
    def index(name=""):
       if 'name' in request.cookies:
           name = request.cookies.get('name')
       return render_template('index.html', name=name)
    ```
4. Signup a new user. You should be directed to the `index` page after a successful signup which should have the content "Welcome <name>".
5. Go to http://127.0.0.1:5000/delete_cookie. You should be directed to the `index` page which should now display "Welcome".

### Exercise 2: Sessions
Login and logout routes have been added to the app, these simply set and delete the session cookie (i.e. no database interaction)
1. Start the Flask app
2. Open Chrome:
    - Open the developer tools
    - Select the Application tab along the top of the toolbar
    - Select Cookies from the sidebar on the left

3. Login:
    - Go to http://localhost:5000/login/ in Chrome.
    - Enter any email address and password and submit the form. 
    - The index page should show the email address you just entered on the login form.
    - You should see the session in the Cookies section of the Developer Tools pane in Chrome.

4. Logout:
    - enter http://localhost:5000/logout/
    - The index page should no longer display the email address in the welcome text.


### Exercise 3: Configure the app to support the login manager extension
1. Create a session object and a Login object for the app in `app/__init__.py`
It will look something like this:
    ```python
    from flask_login import LoginManager
    from flask_sqlalchemy import SQLAlchemy
    
    db = SQLAlchemy()
    login_manager = LoginManager()
    ```
2. Initialise the plugin in the `create_app()` function in the same way as we did for the database e.g. 
    ```python
   def create_app(config_class=DevConfig):
       app = Flask(__name__)
       app.config.from_object(config_class)
   
       db.init_app(app)
       login_manager.init_app(app)
    ```

### Exercise 4: Create a new auth package for our app
1. Create a new Python package for authentication called `auth` inside the `app` package.
2. Create `app/auth/routes.py` and `app/auth/forms.py` 
3. Define a blueprint for auth in in `app/auth/routes.py` e.g.
    ```python
    from flask import Blueprint
   
    bp_auth = Blueprint('auth', __name__)
    ```
4. In `app/__init__.py` register the auth blueprint e.g.
    ```python
    # Register Blueprints
    from app.main.routes import bp_main
    app.register_blueprint(bp_main)

    from app.auth.routes import bp_auth
    app.register_blueprint(bp_auth)
    ```
4. Move the existing sign up and login forms from `app/main/forms.py` to `app/auth/forms.py`. To do this, place the cursor on the form class name, right click 
5. Move the existing signup, login and logout routes from `app/main/routes.py` to `app/auth/routes.py`
5. Stop and restart Flask. Check that signup still works.

### Exercise 5: Modify the User class to inherit the Flask-Login UserMixin class
The UserMixin class will provide default implementations for the following methods:
- `is_authenticated` a property that is True if the user has valid credentials or False otherwise
- `is_active` a property that is True if the user's account is active or False otherwise
- `is_anonymous` a property that is False for regular users, and True for a special, anonymous user
- `get_id()` a method that returns a unique identifier for the user as a string (unicode, if using Python 2)

Edit the User class in models.py to inherit UserMixin, you will also need to add the relevant import e.g. 
 ```python
    from flask_login import UserMixin
        
    class User(UserMixin, db.Model):
 ```

### Exercise 6: Create a login route
A LoginForm class has been created in `app/auth/forms.py`.
A template for the login form has been created in `app/templates/login.html`
1. Add the following helper functions to `app/auth/routes.py`
    ```python
   
    from urllib.parse import urlparse, urljoin

    from flask import request, flash, redirect, url_for
    

    from app import login_manager
    from app.models import User
   
   
   def is_safe_url(target):
       host_url = urlparse(request.host_url)
       redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc 


    def get_safe_redirect():
       url = request.args.get('next')
       if url and is_safe_url(url):
           return url
       url = request.referrer
       if url and is_safe_url(url):
        return url
    return '/'     


    @login_manager.user_loader
    def load_user(user_id):
        """Check if user is logged-in on every page load."""
        if user_id is not None:
           return User.query.get(user_id)
        return None


    @login_manager.unauthorized_handler
    def unauthorized():
        """Redirect unauthorized users to Login page."""
        flash('You must be logged in to view that page.')
        return redirect(url_for('auth.login'))
   
   
    ```
2. Modify the login route to `app/auth/routes.py` e.g.
    ```python
    @bp_auth.route('/login/', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if request.method == 'POST' and form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('Logged in successfully. {}'.format(user.name))
            next = request.args.get('next')
            if not is_safe_url(next):
                return abort(400)
            return redirect(next or url_for('main.index'))
        return render_template('login.html', form=form)
   ```
3. Modify the `logout` route
Remove the code created for the session demo.
Logout should only occur if a user is logged in, so use the `@login_required` decorator e.g.
    ```python
    @bp_auth.route('/logout/')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.')
        return redirect(url_for('main.index'))
    ```
4. Update the navbar in the base template to toggle between log in and logout e.g.
    ```jinja2
   {% if current_user.is_anonymous %}
   <li class="nav-item">
       <a class="nav-link" href="{{ url_for("auth.login") }}">Log in</a>
   </li>
   {% else %}
   <li class="nav-item">
       <a class="nav-link" href="{{ url_for("auth.logout") }}">Log out</a>
   </li>
   {% endif %}
    ```
    The is_anonymous property is one of the attributes that Flask-Login adds to user objects through the UserMixin class.
    The `current_user.is_anonymous` expression will be True only when the user is not logged in.
5. Sign up a new user. Login with that user. The navbar link should have changed to logout and your name should be displayed on the home page.
6. Close and re-open the browser, you should no longer be logged in.

### Exercise 7: Implement the readme feature
By default, when the user closes their browser the Flask Session is deleted and the user is logged out.
“Remember Me” prevents the user from accidentally being logged out when they close their browser.
Flask-Login uses a cookie for this, the duration of which can be set as the REMEMBER_COOKIE_DURATION configuration parameter, or passed when the user logs in.
1. In the login route update the login e.g. 
    ```python
    from datetime import timedelta

    login_user(user, remember=form.remember_me.data, duration=timedelta(minutes=5))

    ```
2. Login. Close the browser. Re-open the browser, you should still be logged in.