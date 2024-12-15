import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Чтение данных
df = pd.read_csv("gym_members_exercise_tracking.csv")

key_metrics = ['Session_Duration (hours)', 'Calories_Burned', 'Workout_Frequency (days/week)', 'BMI']
df = df.dropna(subset=key_metrics)

metrics_to_fill = ['Water_Intake (liters)', 'Fat_Percentage', 'Resting_BPM', 'Avg_BPM']
for metric in metrics_to_fill:
    if metric in df.columns:
        df[metric] = df[metric].fillna(df[metric].median())

categorical_columns = ['Gender', 'Workout_Type', 'Experience_Level']
for column in categorical_columns:
    if column in df.columns:
        df[column] = df[column].fillna(df[column].mode()[0])

# Инициализация Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Gym Members Dashboard"

# Цветовая палитра
colors = [
    '#FFD700', '#FF6347', '#40E0D0', '#FF69B4', '#7FFFD4',
    '#FFA500', '#00FA9A', '#FF4500', '#4682B4', '#DA70D6'
]

# Категориальные и числовые столбцы
cat_columns = ['Gender', 'Workout_Type', 'Workout_Frequency (days/week)', 'Experience_Level']
num_columns = ['Weight (kg)', 'Session_Duration (hours)', 'Calories_Burned', 'BMI']
scatter_features = ['Age', 'Height (m)', 'Max_BPM', 'Avg_BPM', 'Fat_Percentage']

# Layout
app.layout = html.Div([
    html.H1("Gym Members Dashboard", style={'textAlign': 'center', 'color': '#FFD700'}),
    dcc.Tabs([
        # Вкладка 1: Категориальные признаки
        dcc.Tab(style={'color': 'black', 'backgroundColor': 'white'}, 
                label='Categorical Analysis', children=[
            html.Div([
                html.Label("Select Category:"),
                dcc.Dropdown(id='category-dropdown',
                             options=[{'label': col, 'value': col} for col in cat_columns],
                             value=cat_columns[0], 
                             style={'color': 'black', 'backgroundColor': 'white'}),
                dcc.Graph(id='bar-chart'),
                dcc.Graph(id='pie-chart')
            ])
        ]),
        
        # Вкладка 2: Гистограммы для числовых признаков
        dcc.Tab(style={'color': 'black', 'backgroundColor': 'white'}, 
                label='Histograms', children=[
            html.Div([
                html.Label("Select Numerical Feature:"),
                dcc.Dropdown(id='hist-dropdown',
                             options=[{'label': col, 'value': col} for col in num_columns],
                             value=num_columns[0], 
                             style={'color': 'black', 'backgroundColor': 'white'}),
                dcc.Graph(id='histogram')
            ])
        ]),

        # Вкладка 3: Scatter Plots
        dcc.Tab(style={'color': 'black', 'backgroundColor': 'white'},
                label='Scatter Plots', children=[
            html.Div([
                html.Label("Select Feature:"),
                dcc.Dropdown(id='scatter-dropdown',
                             options=[{'label': col, 'value': col} for col in scatter_features],
                             value=scatter_features[0], 
                             style={'color': 'black', 'backgroundColor': 'white'}),
                dcc.Graph(id='scatter-plot')
            ])
        ]),

        # Вкладка 4: Heatmap
        dcc.Tab(style={'color': 'black', 'backgroundColor': 'white'},
                label='Correlation Heatmap', children=[
            html.Div([
                dcc.Graph(id='heatmap')
            ])
        ])
    ])
], style={'backgroundColor': '#000000', 'color': 'white', 'padding': '20px'})

# Callbacks

# Callback для бар-чарта и круговой диаграммы
@app.callback(
    [Output('bar-chart', 'figure'), Output('pie-chart', 'figure')],
    Input('category-dropdown', 'value')
)
def update_categorical_plots(selected_col):
    value_counts = df[selected_col].value_counts()
    
    # Бар-чарт
    bar_fig = px.bar(
        x=value_counts.index, y=value_counts.values,
        title=f'Distribution of {selected_col}',
        labels={'x': 'Categories', 'y': 'Count'},
        color_discrete_sequence=[colors[0]]  # Золотой
    )
    bar_fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    
    # Круговая диаграмма
    pie_fig = px.pie(
        values=value_counts.values, names=value_counts.index,
        title=f'Percentage of {selected_col}',
        color_discrete_sequence=[colors[3], colors[4], colors[1]]  # Разные цвета для секторов
    )
    pie_fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    
    return bar_fig, pie_fig

# Callback для гистограммы
@app.callback(
    Output('histogram', 'figure'),
    Input('hist-dropdown', 'value')
)
def update_histogram(selected_col):
    # Привязка цвета к выбранной колонке
    color_mapping = {
        'Weight (kg)': colors[5],  # Оранжевый
        'Session_Duration (hours)': colors[2],  # Бирюзовый
        'Calories_Burned': colors[1],  # Красный
        'BMI': colors[6]  # Зеленый
    }
    selected_color = color_mapping.get(selected_col, colors[0])
    
    hist_fig = px.histogram(
        df, x=selected_col, title=f'Histogram of {selected_col}',
        color_discrete_sequence=[selected_color]
    )
    hist_fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    return hist_fig


# Callback для Scatter Plot
@app.callback(
    Output('scatter-plot', 'figure'),
    Input('scatter-dropdown', 'value')
)
def update_scatter(selected_col):
    grouped_data = df.groupby(selected_col).size().rename('Count').reset_index()
    scatter_fig = px.scatter(
        grouped_data, x=selected_col, y='Count',
        size='Count', title=f'Scatter Plot of {selected_col} Distribution',
        color_discrete_sequence=[colors[7]]  # Синий
    )
    scatter_fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    return scatter_fig

# Callback для Heatmap
@app.callback(
    Output('heatmap', 'figure'),
    Input('heatmap', 'id')  # Декоративный Input для отображения на старте
)
def update_heatmap(_):
    numeric_df = df.select_dtypes(include=['number'])
    correlation_matrix = numeric_df.corr()

    heatmap_fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='Viridis'
    ))

    heatmap_fig.update_layout(
        title='Correlation Heatmap',
        title_font=dict(color='white'),
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    return heatmap_fig


# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
