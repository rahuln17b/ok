from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DecimalField, FileField, SelectField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = './uploads'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

# Forms
class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    image = FileField('Image')
    submit = SubmitField('Post Item')

class FeedbackForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/browse')
def browse():
    items = Item.query.all()
    return render_template('browse.html', items=items)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_item():
    form = ItemForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = None
        if image:
            filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_item = Item(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            location=form.location.data,
            image_filename=filename
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Item posted successfully!', 'success')
        return redirect(url_for('browse'))
    return render_template('post_item.html', form=form)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        new_feedback = Feedback(comment=form.comment.data, rating=int(form.rating.data))
        db.session.add(new_feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    feedback_list = Feedback.query.all()
    return render_template('feedback.html', form=form, feedback_list=feedback_list)

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

# Initialize database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
