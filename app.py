from flask import Flask, redirect, render_template, request, url_for
import pandas as pd
from sqlalchemy import create_engine


app = Flask(__name__)


engine = create_engine('sqlite:///saved_loader_files.sqlite3', echo=False)

@app.route('/')
def home():
    tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
    return render_template("index.html", tables=tables)


@app.route('/import', methods=['GET', 'POST'])
def new_import():
    if request.method == 'POST':
        df = pd.read_csv(request.files.get('file'))
        file_name = request.files['file'].filename.rsplit('.', 1)[0]
        df.to_sql(file_name, con=engine, if_exists='replace')
        tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
        return redirect(url_for('home'))
    return render_template("import.html")

@app.route('/delete-all', methods=['GET', 'POST'])
def delete_tables():
    if request.method == 'POST':
        tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
        for table in tables:
            engine.execute("DROP TABLE {}".format(table[0]))
        return redirect(url_for('home'))
    return render_template("delete.html")


if __name__ == '__main__':
    app.run(debug=True)
