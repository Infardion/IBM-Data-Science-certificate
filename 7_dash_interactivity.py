import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash
import more_itertools
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Load the data using pandas
spacex_df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


ls_options = [{'label': 'All Sites', 'value': 'ALL'}]
for ls in spacex_df['Launch Site'].unique():
    ls_options.append({'label': ls, 'value': ls})

fig2_df = spacex_df[spacex_df['class']== 1]
fig2_df = fig2_df.groupby('Launch Site')['class'].count().reset_index() 
fig2 = px.pie(fig2_df, values='class', title="Total Success Launches By Site", names=fig2_df['Launch Site'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "SpaceX Launch Records Dashboard"
app.config.suppress_callback_exceptions = True

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    html.Label("Select Launch Site:"),
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=ls_options,
                                        value='ALL',
                                        searchable=True
                                    )
                                ]),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart', style={'display': 'flex'})),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                2500: '2.500', 5000: '5.000', 7500:'7.500', 10000: '10.000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown',component_property='value'))

def success_pie_chart_display(input_site):



    if  input_site=='ALL':
        fig2_df = spacex_df[spacex_df['class']== 1]
        fig2_df = fig2_df.groupby('Launch Site')['class'].count().reset_index() 
        fig2 = px.pie(fig2_df, values='class', title="Total Success Launches By Site", names=fig2_df['Launch Site'])
        return fig2
    else:
        scc_data = spacex_df[spacex_df['Launch Site']==input_site]
        df_pie = scc_data.groupby('class')['Flight Number'].count().reset_index()
        fig1 = px.pie(df_pie, values='Flight Number', title="Success/Failed Launches in {} Launch Site".format(input_site), names=['Fail','Success'])
        return fig1
    


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")])

def success_payload_scatter_chart_display(input_site, input_payload):
    if  input_site=='ALL':
        scatter_df = spacex_df
    else:
        scatter_df = spacex_df[spacex_df['Launch Site']==input_site]

    scatter_df = scatter_df[scatter_df['Payload Mass (kg)']> input_payload[0]]
    scatter_df = scatter_df[scatter_df['Payload Mass (kg)']< input_payload[1]]
    fig3 = px.scatter(scatter_df, x='Payload Mass (kg)',y='class', color='Booster Version Category',title='Correlation between Payload and Success for {} Launching Site(s)'.format(input_site))
    return fig3
    

# Run the app
if __name__ == '__main__':
    app.run_server()

