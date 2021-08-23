import streamlit as st 
import pandas as pd
import altair as alt
import datetime as dt
import plotly.express as px 
import plotly.graph_objects as go
from data import load_data

st.set_page_config(page_title='Evolution of Covid-19 Cases in Canton Zürich per Postal Code')
st.markdown("<style>.reportview-container .main .block-container{ max-width: 2000px; } </style>",unsafe_allow_html=True,) #Makes the page wide: https://discuss.streamlit.io/t/custom-render-widths/81/9
st.title("Evolution of Covid-19 Cases in Canton Zürich per Postal Code")
st.markdown('The data are provided by [@OpenDataZH](https://twitter.com/OpenDataZurich) in their [Covid-19 GitHub repository](https://github.com/openZH/covid_19). All the credit goes to them.')


pd.set_option('display.max_colwidth', None)

    
cases = load_data()
st.markdown(f'_Last data update: {cases.Date.max().strftime("%Y-%m-%d")}_')

colors = ['black', 'silver', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'olive', 'navy', 'orange', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple']
per_capita = st.checkbox("Show cases per 10000 population")

plot_y_axis_title = 'Cases in the last 7 days per 10k population' if per_capita else 'Cases in the last 7 days'
plot_y_axis_column_min = 'NewConfCases_7days_min_per10k' if per_capita else 'NewConfCases_7days_min'
plot_y_axis_column_max = 'NewConfCases_7days_max_per10k' if per_capita else 'NewConfCases_7days_max'
plot_y_axis_column_avg = 'NewConfCases_7days_avg_per10k' if per_capita else 'NewConfCases_7days_avg'
plot_y_axis_column_range = 'NewConfCases_7days_range_str_per10k' if per_capita else 'NewConfCases_7days_range_str'

#st.markdown("### Please choose one or more postal codes")
postal_areas = list(cases.groupby(['Name'], as_index=False).groups.keys())
chosen_postal_areas = st.multiselect("Please choose one or more postal codes",postal_areas,['8193 Eglisau', '8180 Bülach', '8046 Zürich'])

start_date = cases.Date.iloc[0].replace(tzinfo=None)
end_date = cases.Date.iloc[-1].replace(tzinfo=None)
#st.markdown("### Please choose the range of dates")
dates = st.date_input("Please choose the range of dates",[start_date,end_date],start_date,end_date)
if len(dates)<2:
    start_date = dates[0]
else:
    start_date, end_date = dates

cases = cases[ (cases.Date >= pd.Timestamp(start_date, tz="Europe/Paris")) & (cases.Date < pd.Timestamp(end_date + dt.timedelta(days=1), tz="Europe/Paris"))]
cases = cases [ cases['Name'].isin(chosen_postal_areas)]

fig = px.line(cases, x = 'Date', y = plot_y_axis_column_avg, color = 'Name', error_y = None, hover_name='Name', labels= {'Name': 'Municipality', 
    plot_y_axis_column_avg: plot_y_axis_title, 'Week_of_year': 'Week of year', 'NewDeaths_in_district_in_week': 'Weekly deaths in district', 'Area': 'Area (km²)'}, 
    hover_data=['Week_of_year', 'District', 'Area', 'Population', 'NewDeaths_in_district_in_week'])
fig.update_layout({ 'legend_orientation': 'h'})

st.plotly_chart(fig, use_container_width = True)