# import_portfolio

Clone the repo
git clone https://github.com/itsbillw/import_portfolio.git

Create virtual environment
cd import_portfolio
python -m venv venv

Activate virtual environment
source venv/bin/activate

Install requirements
pip install -r requirements.txt

Setup and launch flask environment
export FLASK_APP=app
export FLASK_ENV=development
flask run
