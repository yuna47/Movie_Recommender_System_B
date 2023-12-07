import csv
import os
import secrets
from tkinter import Image

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dc2023:dc5555@210.117.128.202:3306/movieflix'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable=False)
    actor = db.Column(db.Text, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(255), nullable=False)


@app.route('/allMovie')
def allMovie():
    movies = Movie.query.all()
    return render_template('allMovie.html',  movies=movies)


@app.route('/allMovie/<int:movie_id>')
def get_movie_details(movie_id):
    # SQLAlchemy를 사용하여 데이터베이스에서 영화 정보를 가져오기
    movie = Movie.query.get(movie_id)

    if movie:
        # 영화 정보가 있는 경우, 해당 정보를 HTML에 렌더링
        return render_template('movie_details.html', movie=movie)
    else:
        # 영화 정보가 없는 경우, 에러 메시지 또는 기본 정보를 반환
        return "영화 정보를 찾을 수 없습니다."


@app.route('/main')
def main():
    movie = Movie.query.all()
    user_info = session.get('user')
    if user_info:
        username = user_info['username']
        return render_template('main.html', username=username, movie=movie)
    else:
        # 사용자 정보가 없으면 로그인 페이지로 리다이렉션
        return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = {'id': user.id, 'username': user.username}
            return redirect(url_for('main'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('start'))


@app.route('/')
def start():
    return render_template('start.html')


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not username or not email or not password:
            return render_template('signUp.html', error='Please fill in all fields.')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signUp.html')


@app.route('/movieDetails/<int:data_movie_id>')
def movieDetails(data_movie_id):
    # 해당 ID의 영화를 찾음
    return render_template('movieDetails.html', movie_id=data_movie_id)

@app.route('/myfavoGenre')
def myGenre():
    return render_template('my_favorite_genre.html')

# CSV 파일에서 데이터를 읽어와 데이터베이스에 삽입하는 함수
@app.route('/')
def insert_data_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # CSV 파일에서 읽어온 각 행을 데이터베이스에 삽입
            movie = Movie(title=row['title'], genre=row['genre'], director=row['director'],
                          actor=row['actor'], synopsis=row['synopsis'], img=row['img'])
            db.session.add(movie)

        # 변경사항을 데이터베이스에 커밋
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 데이터베이스가 비어있을 경우에만 CSV 파일에서 데이터 삽입
        if not Movie.query.first():
            insert_data_from_csv('./movie_crawl/output/movie.csv')
    app.run(debug=True)