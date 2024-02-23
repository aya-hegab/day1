from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db= SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.Text, nullable=True)
    no_of_pages=db.Column(db.Integer)
    price=db.Column(db.Float)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __str__(self):
        return f"{self.name}"


@app.route("/",endpoint='homepage')
def homePage():
  return render_template("homepage/index.html")

@app.route("/books", endpoint='book.bookslist')
def booksList():
    books = Book.query.all()
    return  render_template("books/index.html",books=books)

vid=0
@app.route("/books/create",methods =['GET', 'POST'], endpoint='book.addNewBook')
def addNewBook():
    global vid
    if request.method == 'POST':
        img=request.files['image']
        img.save("static/books/images/"+str(vid)+"_"+img.filename) 
        book = Book(name=request.form['name'], image=str(vid)+"_"+img.filename,
                     no_of_pages=request.form['no_of_pages'],
                     price=request.form['price'])
        db.session.add(book)
        db.session.commit()
        vid = vid + 1
        return redirect(url_for('book.bookslist'))

    return render_template("books/addnewbook.html")

@app.route("/books/<int:id>", endpoint="book.bookdetails")
def bookDetails(id):
    book = Book.query.get_or_404(id)
    return render_template("books/bookdetails.html", book=book)

@app.route("/bookdelete/<int:id>", endpoint="book.deletebook")
def deleteBook(id):
    # if request.method == 'DELETE':
      book = Book.query.get_or_404(id)  
      os.remove("static/books/images/"+book.image)
      db.session.delete(book)
      db.session.commit()
      return redirect(url_for('book.bookslist'))
    # return "failed"

@app.route("/bookupdate/<int:id>",methods =['GET', 'POST'], endpoint='book.bookupdate')
def bookUpdate(id):
    global vid
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.name = request.form['name']
        
        if request.files['image'].filename != '':
            os.remove("static/books/images/"+book.image)
            img=request.files['image']
            img.save("static/books/images/"+str(vid)+"_"+img.filename) 
            book.image=str(vid)+"_"+img.filename
        book.no_of_pages = request.form['no_of_pages']
        book.price = request.form['price']
        db.session.commit()
        vid = vid + 1
        return redirect(url_for('book.bookdetails', id=book.id))

    return render_template("books/bookupdate.html",book=book)

@app.errorhandler(404)
def get_404(error):
    return render_template("error404.html")

if __name__ == '__main__':
  app.run(debug=True)