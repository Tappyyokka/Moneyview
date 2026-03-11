# MoneyView 💰

MoneyView is a personal finance tracking web application that helps users monitor their income, expenses, savings, and debts in one dashboard. The application also includes an AI-based advisor that provides insights and financial suggestions.

## Features

* User authentication (login & registration)
* Multi-step financial onboarding
* Expense and income tracking
* Financial dashboard with charts
* Debt and savings monitoring
* AI financial advisor
* Data stored securely in AWS RDS
* Hosted on AWS EC2 using Nginx and Gunicorn

## Tech Stack

Frontend:

* HTML
* CSS
* JavaScript
* Chart.js

Backend:

* Python
* Flask

Infrastructure:

* AWS EC2 (server hosting)
* AWS RDS (database)
* Gunicorn (WSGI server)
* Nginx (reverse proxy)

## Architecture

User → Nginx → Gunicorn → Flask → AWS RDS

## Project Structure

```
moneyview/
│
├── app.py
├── database/
│   └── db.py
├── templates/
├── static/
├── venv/
└── README.md
```

## Installation (Local)

Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/Moneyview.git
```

Go into the project directory:

```
cd moneyview
```

Create virtual environment:

```
python -m venv venv
```

Activate environment:

Windows

```
venv\Scripts\activate
```

Linux

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the application:

```
python app.py
```

## Deployment

The application is deployed on AWS:

* EC2 instance for hosting
* Gunicorn for running Flask
* Nginx as reverse proxy
* AWS RDS MySQL database

## Future Improvements

* AI financial prediction
* Budget alerts
* Investment tracking
* Mobile responsive UI
* Email notifications

## Author

Abhinand M
