from flask import Flask, render_template, request
import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

app = Flask(__name__)
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')


class ExpenseTracker:
    def __init__(self):
        self.expenses = {}

    def add_expense(self, category, amount):
        if category in self.expenses:
            self.expenses[category] += amount
        else:
            self.expenses[category] = amount

    def show_expenses(self):
        total_expense = 0
        result = "Expense Tracker:<br>"
        for category, amount in self.expenses.items():
            result += f"{category}: ${amount}<br>"
            total_expense += amount
        result += f"Total: ${total_expense}<br>"
        return result

    def remove_expense(self, category, amount):
        if category in self.expenses:
            if amount >= self.expenses[category]:
                del self.expenses[category]
            else:
                self.expenses[category] -= amount
            return f"${amount} removed from {category}"
        else:
            return "Category not found."


tracker = ExpenseTracker()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        action = request.form['action']

        if action == 'Add':
            tracker.add_expense(category, amount)
        elif action == 'Remove':
            tracker.remove_expense(category, amount)

    expenses = tracker.show_expenses()
    return render_template('index.html', expenses=expenses)


@dash_app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('update-button', 'n_clicks')]
)
def update_bar_chart(n_clicks):
    categories = list(tracker.expenses.keys())
    amounts = list(tracker.expenses.values())

    trace = go.Bar(
        x=categories,
        y=amounts
    )
    layout = go.Layout(
        title='Expense Breakdown',
        xaxis=dict(title='Categories'),
        yaxis=dict(title='Amount')
    )
    return {'data': [trace], 'layout': layout}


@dash_app.callback(
    dash.dependencies.Output('total-expense', 'children'),
    [dash.dependencies.Input('update-button', 'n_clicks')]
)
def update_total_expense(n_clicks):
    total_expense = sum(tracker.expenses.values())
    return f'Total Expense: ${total_expense}'


@dash_app.callback(
    dash.dependencies.Output('table', 'children'),
    [dash.dependencies.Input('update-button', 'n_clicks')]
)
def update_table(n_clicks):
    df = pd.DataFrame({'Category': list(tracker.expenses.keys()), 'Amount': list(tracker.expenses.values())})
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))]
    )


@dash_app.callback(
    dash.dependencies.Output('update-button', 'n_clicks'),
    [dash.dependencies.Input('category', 'value'), dash.dependencies.Input('amount', 'value')]
)
def update_expense(category, amount):
    if category and amount:
        tracker.add_expense(category, float(amount))
        return 0


@dash_app.callback(
    dash.dependencies.Output('remove-button', 'n_clicks'),
    [dash.dependencies.Input('category', 'value'), dash.dependencies.Input('amount', 'value')]
)
def remove_expense(category, amount):
    if category and amount:
        tracker.remove_expense(category, float(amount))
        return 0


dash_app.layout = html.Div([
    html.H1('Expense Tracker Dashboard'),
    html.Div([
        html.Label('Category:'),
        dcc.Input(id='category', type='text'),
        html.Label('Amount:'),
        dcc.Input(id='amount', type='number'),
        html.Button('Add', id='update-button', n_clicks=0),
        html.Button('Remove', id='remove-button', n_clicks=0)
    ]),
    dcc.Graph(id='bar-chart'),
    html.Div(id='total-expense'),
    html.Div(id='table')
])

if __name__ == '__main__':
    app.run(debug=True)
