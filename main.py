from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from sqlalchemy import exc as SQLAlchemyException

import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ppdb:swordfish@ppdbmysql.ct4sai8mxgm9.us-east-2.rds.amazonaws.com:3306/ppdb'
app.config['SECRET_KEY'] = secrets.token_bytes(32)
app.config['WTF_CSRF_SECRET_KEY'] = secrets.token_bytes(32)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    short_desc = db.Column(db.String(80), unique=False, nullable=False)
    long_desc = db.Column(db.String(280), unique=False, nullable=False)
    img = db.Column(db.String(280), unique=False, nullable=False)

    def __repr__(self):
        return 'Pizza, id: {}, name: {}, price: {}'.format(self.id, self.name, self.price)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String(80), unique=False, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey(Pizza.id), nullable=False)
    pizza_count = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return 'Order, id: {}, name: {}, address: {}. Pizza: {}, count: {}'.format(self.id, self.name, self.address,
                                                                                   self.pizza_id, self.pizza_count)

class PizzaForm(FlaskForm):
    pizza_name = StringField('pizza_name', validators=[DataRequired()])
    price = IntegerField('price', validators=[DataRequired(), NumberRange(min=500)])
    short_desc = StringField('short_desc', validators=[DataRequired()])
    long_desc = StringField('long_desc', validators=[DataRequired()])
    img_url = StringField('img_url', validators=[DataRequired()])

@app.route('/')
def index():
    try:
        orders = Order.query.all()
        pizzas = Pizza.query.all()
    except SQLAlchemyException.OperationalError:
        orders = []
    return render_template('index.html', orders=orders, pizzas=pizzas)  # Renders template, with list queried from db


@app.route('/pizza', methods=['GET', 'POST'])
def new_pizza():
    try:
        pizzas = Pizza.query.all()
    except SQLAlchemyException.OperationalError:
        pizzas = []
    form = PizzaForm(request.form)

    if form.validate_on_submit():
        new_pizza = Pizza(name=form.pizza_name.data, price=form.price.data, short_desc=form.short_desc.data, long_desc=form.long_desc.data, img=form.img_url.data)
        if new_pizza:
            db.session.add(new_pizza)
            db.session.commit()

        return redirect('/pizza')


    return render_template('pizza.html', pizzas=pizzas, form=form)

if __name__ == '__main__':
    print("wololo")
    app.run(port=8080, debug=True)
    # Note requires a run before it saves db (possibly only an issue with sqlite)
    # Doesn't update with schema changes so watchout for that
    db.create_all()
