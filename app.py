from flask import Flask, render_template, request
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
        df.to_sql(input_filename, con=engine, if_exists='replace')
        return render_template("index.html", tables=tables)
    return render_template("import.html")


if __name__ == '__main__':
    app.run(debug=True)
