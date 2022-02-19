import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from joblib import load
import pandas as pd

import PreprocessModule as pm

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(
    [
        dcc.Store(id="store"),
        html.Hr(),
        html.H2('Wykrywanie mowy nienawiści w tweetach',
                style={'textAlign': 'center'}),
        html.Hr(),
        html.Br(),

        html.Div(children=[
            dbc.Textarea(id='input_text',
                         className="mb-3",
                         placeholder="Tutaj wklej treść tweeta w języku polskim",
                         rows=10),
        ],
            style={'textAlign': 'center'}
        ),

        dbc.Button(
                "Weryfikuj",
                id="ver_button",
                color="primary",
                className="d-grid gap-2 col-6 mx-auto",
                n_clicks=0
        ),

        html.Br(),

        dbc.Alert(children=[
                html.H4("Werdykt:", className="alert-heading"),
                html.H2(id='verdict'),
                html.Hr(),
            ],
            color="secondary"
        ),
    ]
)

#------------------------------------------------------------------
@app.callback(
    Output(component_id='verdict', component_property='children'),
    Input(component_id='ver_button', component_property='n_clicks'),
    State(component_id='input_text', component_property='value'),
)
def get_predictions(n_clicks, text):
    content = str(text)
    if n_clicks is not None and text is not None:
        content = pm.RemoveHashtags(content)
        content = pm.RemoveMentions(content)
        content = pm.RemovePunctuation(content)
        content = pm.Lemmatize(content)
        content = pm.RemoveStopWords(content)
        content = pm.LowerCase(content)

        df = pd.DataFrame([[content]], columns=['Text'])

        vectorizer = load('models/vectorizer.joblib')
        input = vectorizer.transform(df['Text'])

        svcClassifier = load('models/svc.joblib')

        result = svcClassifier.predict(input)[0]

        if result:
            return 'Treść podanego tweeta prawdopodobnie jest obraźliwa'
        else:
            return 'Treść podanego tweeta prawdopodobnie nie jest obraźliwa'
    else:
        return ' '
#------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)