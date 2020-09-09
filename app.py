from flask import Flask, flash, make_response, redirect, render_template, request, url_for
import pandas as pd
from sqlalchemy import create_engine


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}
engine = create_engine('sqlite:///saved_loader_files.sqlite3', echo=False)


@app.route('/')
def home():
    # TODO:
    # 1. Message when no files uploaded
    # 2. Edit imported file - map columns, replace values

    tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
    return render_template("index.html", tables=tables)


@app.route('/view/<table_name>', methods=("POST", "GET"))
def view_table(table_name):
    df = pd.read_sql("select * from {}".format(table_name), con=engine, index_col="index")
    table_title = table_name.replace("_"," ").title()
    return render_template('view.html',  tables=[df.to_html(index=False, classes='data')], title=table_title)


@app.route('/import', methods=['GET', 'POST'])
def new_import():
    # TODO:
    # 1. Check for valid data
    # 2. Parse file into loader format

    if request.method == 'POST':
        import_file = request.files.get('file')
        file_name = request.files['file'].filename.rsplit('.', 1)[0]
        file_extension = request.files['file'].filename.rsplit('.', 1)[1]

        if file_extension in ALLOWED_EXTENSIONS:
            if file_extension == "csv":
                df = pd.read_csv(import_file)
            else:
                df = pd.read_excel(import_file)
            df.to_sql(file_name, con=engine, if_exists='replace')
        else:
            flash("Unsupported filetype. Please upload csv or excel file")
            return redirect(url_for('new_import'))
        return redirect(url_for('home'))
    return render_template("import.html")


@app.route('/download/<table_name>', methods=['GET', 'POST'])
def download_table(table_name):
    df = pd.read_sql("select * from {}".format(table_name), con=engine, index_col="index")
    resp = make_response(df.to_csv(index=False))
    resp.headers["Content-Disposition"] = "attachment; filename={}.csv".format(table_name)
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route('/delete/<table_name>', methods=['GET', 'POST'])
def delete_one_table(table_name):
    engine.execute("DROP TABLE {}".format(table_name))
    return redirect(url_for('home'))


@app.route('/delete', methods=['GET', 'POST'])
def delete_all_tables():
    if request.method == 'POST':
        tables = engine.execute("select name from sqlite_master where type = 'table'").fetchall()
        for table in tables:
            engine.execute("DROP TABLE {}".format(table[0]))
        return redirect(url_for('home'))
    return render_template("delete.html")


if __name__ == '__main__':
    app.run(debug=True)
