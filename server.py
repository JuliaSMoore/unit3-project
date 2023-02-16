from flask import Flask, render_template, redirect, flash, request, session
import jinja2
from melons import get_all, get_by_id
from customers import get_by_username
from forms import LoginForm

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def homepage ():
    return render_template("base.html")

@app.route("/melons")
def get_all_melons():
    melons = get_all()
    return render_template("melons.html", melons = melons)

@app.route("/melon/<melon_id>")
def get_one_melon(melon_id):
    melon = get_by_id(melon_id)
    return render_template("melon.html", melon = melon)

@app.route("/delete/<melon_id>")
def delete_from_cart(melon_id):
    melon = get_by_id(melon_id)
    cart = session.get("cart", {})
    del cart[melon.melon_id]
    session.modified = True
    flash("Item deleted!")
    return redirect("/cart")

@app.route("/increase/<melon_id>")
def increase_quantity(melon_id):
    cart = session['cart']
    cart[melon_id] = cart.get(melon_id) + 1
    session.modified = True
    return redirect("/cart")

@app.route("/decrease/<melon_id>")
def decrease_quantity(melon_id):
    cart = session['cart']
    cart[melon_id] = cart.get(melon_id) - 1
    session.modified = True
    return redirect("/cart")

@app.route("/add_to_cart/<melon_id>")
def add_to_cart(melon_id):
    if 'username' not in session:
        return redirect("/login")

    if "cart" not in session:
        session["cart"] = {}
    cart = session['cart']
    cart[melon_id] = cart.get(melon_id, 0) + 1
    session.modified = True
    flash(f"Melon {melon_id} successfully added to cart.")
    return redirect("/cart")

@app.route("/cart")
def view_cart():
    if 'username' not in session:
        return redirect("/login")

    order_total = 0
    cart_melons = []
    cart = session.get("cart", {})

    for melon_id, qty in cart.items():
        melon = get_by_id(melon_id)
        total_cost = qty * melon.price
        order_total += total_cost

        melon.quantity = qty
        melon.total_cost = total_cost

        cart_melons.append(melon)

    return render_template("cart.html", cart_melons=cart_melons, order_total=order_total)

@app.route("/empty-cart")
def empty_cart():
    session["cart"] = {}

    return redirect("/cart")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = get_by_username(username)

        if not user or user['password'] != password:
            flash("Invalid username or password")
            return redirect('/login')

        session["username"] = user['username']
        flash("Logged in.")
        return redirect("/melons")

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    del session["username"]
    flash("Logged out!")
    return redirect("/login")

@app.errorhandler(404)
def error_404(e):
   return render_template("404.html")

if __name__ == "__main__":
   app.env = "development"
   app.run(debug = True, port = 8000, host = "localhost")