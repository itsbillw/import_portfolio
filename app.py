from flask import Flask, flash, make_response, redirect, render_template, request, url_for
import pandas as pd
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename

from transform_loader import combine_loaders, loader_prep


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


engine = create_engine('sqlite:///data/saved_loader_files.sqlite3', echo=False)


@app.route('/', methods=['GET', 'POST'])
def home():
    # TODO:
    # 1. Message when no files uploaded
    # 2. Edit imported file - map columns, replace values

    tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()

    if request.method == 'POST':
        table_list = request.form.getlist('get_table')
        for table in table_list:
            engine.execute("DROP TABLE '{}'".format(table))
        return redirect(url_for('home'))

    return render_template("index.html", tables=tables)


@app.route('/view/<table_name>', methods=("POST", "GET"))
def view_table(table_name):
    df = pd.read_sql("select * from '{}'".format(table_name), con=engine)
    table_title = table_name.replace("_"," ").title()
    return render_template('view.html',  table=df.to_html(index=False, classes='data'), title=table_title)


@app.route('/import', methods=['GET', 'POST'])
def new_import():
    # TODO:
    # 1. Check for valid data
    # 2. Parse file into loader format
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            filename = file_name.rsplit('.', 1)[0]
            file_extension = file_name.rsplit('.', 1)[1]
            if file_extension == "csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            df = loader_prep(df)
            df.to_sql(filename, con=engine, if_exists='replace', index=False)
        else:
            flash("Unsupported filetype. Please upload csv or excel file")
            return redirect(request.url)
        return redirect(url_for('home'))
    return render_template("import.html")


@app.route('/combine', methods=['GET', 'POST'])
def combine_tables():
    tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
    if request.method == 'POST':
        table_list = request.form.getlist('get_table')
        new_name = request.form.get('table_name')
        if len(table_list) >= 1 and new_name != '':
            df = combine_loaders(table_list)
            df.to_sql(new_name, con=engine, if_exists='replace', index=False)
        return redirect(url_for('home'))
    return render_template("combine.html", tables=tables)


@app.route('/download/<table_name>', methods=['GET', 'POST'])
def download_table(table_name):
    df = pd.read_sql("select * from '{}'".format(table_name), con=engine)
    resp = make_response(df.to_csv(index=False))
    resp.headers["Content-Disposition"] = "attachment; filename={}.csv".format(table_name)
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route('/delete/<table_name>', methods=['GET', 'POST'])
def delete_one_table(table_name):
    engine.execute("DROP TABLE '{}'".format(table_name))
    return redirect(url_for('home'))


@app.route('/delete', methods=['GET', 'POST'])
def delete_all_tables():
    tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
    if request.method == 'POST':
        table_list = request.form.getlist('get_table')
        for table in table_list:
            engine.execute("DROP TABLE '{}'".format(table))
        return redirect(url_for('home'))
    return render_template("delete.html", tables=tables)


if __name__ == '__main__':
    app.run(debug=True)
