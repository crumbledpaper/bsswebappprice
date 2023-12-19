# Run the server
Install requirements
```bash
pip install -r requirements.txt
```
Run server
```bash
flask run
or
flask --app wsgi.py run
```
## Run server using Gunicorn <strong>(Recommended)</strong>
<br>Create a virtual enviroment `python3 -m venv myprojectenv`
```bash
source myprojectenv/bin/activate
gunicorn --bind 0.0.0.0:5000 wsgi:app
```
# Modules Description
 * **auth.py** 
Takes care of the authorization of the login session. Checks passwords against the username, directs to signup page if the user is not found in the users table, and stores the signup info into a hashed DB.  Also holds the routes for authentication html like login, signup, logout
 * **main.py** 
All the routes for the particular application is mentioned here in main file. To run the application use the command:
```bash
python main.py
```
Mention `@login_required` before defining a function for the route to make it limited to the user. Example below
```python
@main.route("/dashboard/")
@login_required
def dashboard():
    return render_template("dashboard.html")
```
 * **model.py** 
The column name and character limits are mentioned in this file, basically creating an SQL table to home the collected signup information.
<br>-> If you made changes to models.py then run these commands:
<br> &nbsp;  &nbsp;  &nbsp; `flask db migrate`
<br> &nbsp;  &nbsp;  &nbsp; `flask db upgrade`
<br>-> If you change or delete database then run these command:
<br> &nbsp;  &nbsp;  &nbsp; `flask db upgrade`
<br>For more information check here [flask-migrate](https://flask-migrate.readthedocs.io/en/latest/)
