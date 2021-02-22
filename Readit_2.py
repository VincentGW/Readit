from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        post_title = request.form['title']
        post_author = request.form['author']
        post_subreddit = request.form['subreddit']
        entered_book = Book.query.filter_by(author=post_author).filter_by(title=post_title).first()
        if entered_book is None: #If the entered book doesn't exist, add it
            new_book_recommendation = Book(title=post_title, author=post_author)
            db.session.add(new_book_recommendation)
            db.session.commit()
            entered_book = Book.query.filter_by(author=post_author).filter_by(title=post_title).first()

        if Subreddit.query.filter_by(subreddit=post_subreddit).filter_by(book_id=entered_book.id).first() is not None:
            entry = Subreddit.query.filter_by(subreddit=post_subreddit).filter_by(book_id=entered_book.id).first()
            entry.numvotes += 1
            db.session.commit()
            return redirect('/')

        new_subreddit = Subreddit(subreddit=post_subreddit, book_id=entered_book.id)
        try:
            db.session.add(new_subreddit)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your book recommendation.'
    else:
        subreddit_database = Subreddit.query.order_by(Subreddit.subreddit).order_by(Subreddit.numvotes.desc()).all()
        cursor = Subreddit.query.order_by(Subreddit.subreddit).order_by(Subreddit.numvotes.desc()).first()
        if cursor is None:
            return render_template('index_empty.html')
        else:
            cursor = cursor.subreddit
            inner_dict1 = {}
            inner_dict2 = {}
            hidden_dict = {}
            final_dict = {}
            for row in subreddit_database:
                book_id = row.book_id
                vote = row.numvotes
                subname = row.subreddit
                book_data = Book.query.filter_by(id=book_id).first()
                book_title = book_data.title
                if len(inner_dict2) < 5:
                    if cursor != subname:
                        hidden_dict[cursor] = inner_dict1
                        final_dict[cursor] = inner_dict2
                        cursor = subname
                        inner_dict1 = {}
                        inner_dict2 = {}
                        inner_dict1[book_id] = vote
                        inner_dict2[book_title] = vote
                    else:
                        inner_dict1[book_id] = vote
                        inner_dict2[book_title] = vote
                else:
                    if cursor != subname:
                        hidden_dict[cursor] = inner_dict1
                        final_dict[cursor] = inner_dict2
                        cursor = subname
                        inner_dict1 = {}
                        inner_dict2 = {}
                        inner_dict1[book_id] = vote
                        inner_dict2[book_title] = vote
                    else:
                        pass

        hidden_dict[cursor] = inner_dict1
        final_dict[cursor] = inner_dict2

    return render_template('index.html', hidden_dict=hidden_dict, final_dict=final_dict)

    def __repr__(self):
        return'<Entry %r>' % self.id

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    subreddits = db.relationship('Subreddit', backref='book', lazy=True)

class Subreddit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subreddit = db.Column(db.String(40), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    numvotes = db.Column(db.Integer, default=1)

if __name__ == '__main__':
    app.run(debug=True)