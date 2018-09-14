from flask import Flask, render_template, flash

app = Flask(__name__)
app.secret_key = 'dev'

@app.route('/')
def frontpage():
	return render_template("frontpage.html")

@app.errorhandler(404)
def page_not_found(e):
	flash('Not ready yet!')
	return render_template("404.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
