from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 's3cr3t-k3y-f0r-0r4ng3s'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oranges.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imyachelika = db.Column(db.String(80), unique=True, nullable=False)
    pochta = db.Column(db.String(120), unique=True, nullable=False)
    parol_hash = db.Column(db.String(128))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', the_title='Главная - Торговля апельсинами', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        imyachelika = request.form.get('логин')
        pochta = request.form.get('почта')
        parol = request.form.get('пароль')
        if User.query.filter_by(imyachelika=imyachelika).first() or User.query.filter_by(pochta=pochta).first():
            flash('Пользователь с таким именем или email уже существует.')
            return redirect(url_for('register'))
        hashed = generate_password_hash(parol)
        new_user = User(imyachelika=imyachelika, pochta=pochta, parol_hash=hashed)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно. Теперь войдите.')
        return redirect(url_for('login'))
    return render_template('register.html', the_title='Регистрация')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        imyachelika = request.form.get('логин')
        parol = request.form.get('пароль')
        user = User.query.filter_by(imyachelika=imyachelika).first()
        if user and check_password_hash(user.parol_hash, parol):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль.')
    return render_template('login.html', the_title='Вход')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Product.query.first():
            db.session.add_all([
                Product(name='Апельсин Валенсия', description='Сладкий и сочный.', price=250.0, quantity=100, category='розница'),
                Product(name='Апельсин Навел', description='Без косточек, легко чистится.', price=300.0, quantity=80, category='розница'),
                Product(name='Красный апельсин', description='Насыщенный вкус, красная мякоть.', price=400.0, quantity=50, category='опт')
            ])
            db.session.commit()
    app.run(debug=True)