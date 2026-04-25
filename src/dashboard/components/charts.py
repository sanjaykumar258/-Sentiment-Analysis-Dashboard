# Reusable chart functions if needed
# Currently implemented directly in page files using Plotly Express for simplicity
import plotly.express as px
from src.dashboard.styles import PLOTLY_TEMPLATE

def create_donut_chart(df, names, values, title, color_map=None):
    fig = px.pie(df, names=names, values=values, hole=0.4, title=title, color=names, color_discrete_map=color_map)
    fig.update_layout(template=PLOTLY_TEMPLATE)
    return fig
