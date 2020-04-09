CircleCI Build status: [![CircleCI](https://circleci.com/gh/justinattw/Group1_Mealtime.svg?style=svg)](https://circleci.com/gh/justinattw/Group1_Mealtime)

# Mealtime

**Personal meal-planning and cooking assistant**

A digital cookbook/ meal-planning service web application.

Allow users to browse a catalog of recipes based on user specifications of food types.

Allows logged-in users to create meal-plans, add items to meal-plans, and additional functionalities related to meal-planning.

- GitHub repository: https://github.com/justinattw/Group1_Mealtime
- Video demonstration:
- Heroku application: https://comp0034-mealtime.herokuapp.com

---

Runs on the Flask web framework and uses SQL Alchemy to connect database to application models, so it can be conveniently re-configured to run in many servers and database environments.

#### Database

We have elected to use SQLite database for the application. The database stores information on recipes, meal-plans, and users.

##### Re-creating the database

With the current repository, there is no need to re-create the database unless there are reasons to restart with a fresh database.

To overhaul the database (start with a fresh database with no users and BBC Good Foods web-scraped recipes)

Caution: this will delete existing users.

1. Navigate to `db` directory
2. Delete `mealtime.sqlite`
3. Run `create_db.py` (ETA: 10-15 minutes)

To connect to the database, define the database URI in the configuration file `config.py`.

**Disclaimer**: The recipes in the database are taken from BBC Good Foods. The purpose of populating the database this way is purely for functionality and as proof-of-concept, using the scraped recipes as dummy data. There may be inconsistencies/ incorrect recipes due to the nature of web-scraping, and errors which we have no tested for (as this is not the focus of the demonstration of the application).

___

#### Config files

The application configurations are stored in `config.py`. There will be a main configuration `Config(object)`, and three other configurations (production, development and testing) that inherits from the main configuration.

In the main configuration, you will have to set Flask and WTForms secret keys.

    """Set Flask base configuration"""
    SECRET_KEY = 'ENTER_YOUR_SECRET_KEY'
    
    ...

    # Forms config
    WTF_CSRF_SECRET_KEY = 'ENTER_YOUR_OTHER_SECRET_KEY'

With each of the three alternate configurations, re-define Flask variables and database URI.

___

#### Install Python and dependencies

The application was developed in Python 3.

To install Flask and other Python code dependencies (outside of Pycharm), the easiest way is using PIP.

`pip install -r requirements.txt`


## Running the app

You can start the mealtime application by running run.py

`python3 run.py`

If everything is working properly you should see

`Runnin on http://0.0.0.0:5000/ (Press CTRL+C to quit`

This means the app is up and running and serving requests. You should be able to visit the URL to access the application.


#### Issues and suggestions

If you run into any issues running the app or have any ideas for improvements, feel free to open an issue on GitHub or contact any of the following:

- ethmacc@gmail.com
- spandoboy@gmail.com
- justinattw@gmail.com