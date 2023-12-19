from flask import Blueprint, render_template, request, send_from_directory, redirect, url_for, Response
from flask_login import login_required, current_user
from app import create_app, db
from scraper import get_bonita_smoke_shop_price, get_neptune_cigar_price, get_cigars_international_price
import auth
main = Blueprint('main', __name__)


#index page
@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("dashboard")
    return render_template("index.html")

#login page
@main.route("/login")
def login():
    return render_template("login.html")


#logout page
@main.route("/logout/")
def logout():
    return render_template("logout.html")



#This web page will be loaded on successful login
@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user.name)



@main.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    product_name = request.form.get('product_name')

    # if not product:
    #     flash('Product not found')
    #     return redirect(url_for('main.dashboard')) # use 'main.dashboard' instead of 'dashboard'

    # Scrape the prices
    products = []
    try:
        products.append(get_bonita_smoke_shop_price(product_name))
    except Exception as e:
        print('Error: loading Bonita Smoke', e)
    
    try:
        products.append(get_neptune_cigar_price(product_name))
    except Exception as e:
        print('Error: loading Neptune Cigar', e)
    
    try:
        products.append(get_cigars_international_price(product_name))
    except Exception as e:
        print('Error: loading Cigars International', e)

    # db.session.commit()

    return render_template('product_prices.html', 
        product_name=product_name.title(), 
        products=products, 
        user=current_user.name
        )






# we initialize our flask app using the __init__.py function
app = create_app()

#jinja zip for multiple iteration in html table
app.jinja_env.filters['zip'] = zip

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()  # create the database
    app.run(port=8080)  # run the flask app
    # app.run(port=8080, debug=True)  # run the flask app on debug mode
