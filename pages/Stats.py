import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Config trang -----------------------------------------
st.set_page_config(
    page_title="PR Dashboard",
    page_icon="🔮",
    layout="wide",
)

# Tạo tiêu đề -----------------------------------------

st.image('https://i.pinimg.com/564x/b4/10/1e/b4101eb5bc27a62b8f681bd03da9ffff.jpg')
st.markdown("<h1 style='text-align: center; color: #B799FF;'>Performance Review Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---", unsafe_allow_html=True)

#-------------------------------------------------------
billable_projects = ["YGM", "PRO", "US-", "CG-", "CBV", "NRS", "PGA", "RMA"]
ultilized_projects = ["SMV", "PAT", "ASE", "CGR", "USG"]
st.info(
    f"""
    **Billable Projects:** {', '.join(billable_projects)}\n
    **Utilized Projects:** {', '.join(ultilized_projects)}
    """
)

selected_option = st.selectbox("Choose a person", ["trungmai", "phuongpham", "khangnguyen", "khoicao", "locnguyen", "toanpham"])

df = pd.read_excel(f"./data/{selected_option}.xls", sheet_name="Report")
df.drop(df.tail(1).index, inplace=True)
df.drop("Unnamed: 0", axis=1, inplace=True)
df = df.fillna(0)

#-------------------------------------------------------
st.title('Search Tasks')
col1, col2 = st.columns(2)
selected_hours = st.slider('Select an hour range:', 0.0, 20.0, step=0.25)
st.write(f'Selected Range: {selected_hours}')
with col1:
    search_term = st.text_input('Search Task:', '')
with col2:
    search_description = st.text_input('Search Description:', '')

if search_term == "":
    st.dataframe(
        df[(df["Issue"].str.contains(search_description, case=False)) & (df["Logged"] > selected_hours)][["Issue", "Key", "Logged"]]
    )
elif search_description == "":
    st.dataframe(
        df[(df["Key"].str.contains(search_term, case=False)) & (df["Logged"] > selected_hours)][["Issue", "Key", "Logged"]]
    )
else:
    st.dataframe(
        df[(df["Key"].str.contains(search_term, case=False)) & (df["Issue"].str.contains(search_description, case=False)) & (df["Logged"] > selected_hours)][["Issue", "Key", "Logged"]]
    )

#-------------------------------------------------------
st.markdown(f"### Tổng số task đã thực hiện trong thời gian qua: {df.shape[0]} tasks")

billable_df = df[df["Key"].apply(lambda x: x[:3] in billable_projects)]
ultilized_df = df[df["Key"].apply(lambda x: x[:3] in ultilized_projects)]

# st.markdown(f"### Tổng số task billable: {billable_df.shape[0]}")
# st.markdown(f"### Tổng số task utilized: {billable_df.shape[0] + ultilized_df.shape[0]}")

#-------------------------------------------------------
tasks_data = {"utilized": billable_df.shape[0] + ultilized_df.shape[0]}
tasks_data["non-utilized"] = len(df) - tasks_data["utilized"]

st.title('Number of tasks')

fig = go.Figure()
fig.add_trace(go.Bar(x=list(tasks_data.keys()), y=list(tasks_data.values()), text=list(tasks_data.values()), textposition='outside'))
fig.update_layout(
    xaxis_title='Category',
    yaxis_title='Count',
)
st.plotly_chart(fig)

#-------------------------------------------------------
tasks_data_pie = {"billable": billable_df.shape[0], "utilized": ultilized_df.shape[0]}
tasks_data_pie["non-utilized"] = len(df) - tasks_data_pie["utilized"] - tasks_data_pie["billable"]
fig = go.Figure()
fig.add_trace(go.Pie(labels=list(tasks_data_pie.keys()), values=list(tasks_data_pie.values()),
                     textinfo='label+percent', pull=[0.1, 0, 0]))  # Adjust the pull parameter as needed
st.plotly_chart(fig)

# st.markdown(f"### Tổng thời gian log billable: {round(sum(billable_df['Logged']),2)} h")
# st.markdown(f"### Tổng thời gian log utilized: {round(sum(billable_df['Logged']) + sum(ultilized_df['Logged']),2)} h")

#-------------------------------------------------------
hours_data = {"utilized": round(sum(billable_df['Logged']) + sum(ultilized_df['Logged']), 2)}
hours_data["non-utilized"] = round(sum(df["Logged"]) - hours_data["utilized"], 2)
st.title('Hours Logged')
fig = go.Figure()
fig.add_trace(go.Bar(x=list(hours_data.keys()), y=list(hours_data.values()), text=list(hours_data.values()), textposition='outside'))
fig.update_layout(
    xaxis_title='Category',
    yaxis_title='Hours',
)
st.plotly_chart(fig)

#-------------------------------------------------------
hours_data_pie = {"billable": round(sum(billable_df['Logged']), 2), "utilized": round(sum(ultilized_df['Logged']), 2)}
hours_data_pie["non-utilized"] = round(sum(df["Logged"]) - hours_data_pie["utilized"] - hours_data_pie["billable"], 2)
fig = go.Figure()
fig.add_trace(go.Pie(labels=list(hours_data_pie.keys()), values=list(hours_data_pie.values()),
                     textinfo='label+percent', pull=[0.1, 0, 0]))  # Adjust the pull parameter as needed
st.plotly_chart(fig)

#-------------------------------------------------------
df["Project"] = df["Key"].apply(lambda key: key[:3])
st.title('Project Distribution')
fig = go.Figure()
fig.add_trace(go.Bar(x=df["Project"].value_counts().index, y=df["Project"].value_counts().values, text=df["Project"].value_counts().values, textposition='outside'))
fig.update_layout(
    xaxis_title='Project',
    yaxis_title='Hours',
)
st.plotly_chart(fig)

#-------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Pie(labels=df["Project"].value_counts().index, values=df["Project"].value_counts().values,
                     textinfo='label+percent', pull=[0.1, 0, 0]))  # Adjust the pull parameter as needed
st.plotly_chart(fig)

#-------------------------------------------------------
st.title('Project Hours Distribution')
project_hours_data = []
for proj in df["Project"].value_counts().index:
    proj_df = df[df["Project"] == proj]
    project_hours_data.append((proj, round(sum(proj_df["Logged"]), 2)))
project_hours_df = pd.DataFrame(project_hours_data, columns=['Project', 'Hours'])
fig = px.pie(project_hours_df, names='Project', values='Hours', title='Project Hours Distribution')
st.plotly_chart(fig)

#-------------------------------------------------------
filtered_df = billable_df[billable_df["Logged"] > 5][["Key", "Logged"]]
st.title('Billable Tasks with More than 5 Hours Logged')
fig = px.bar(
    filtered_df,
    x="Key",
    y="Logged",
    text="Logged",
    title="Billable tasks with more than 5 hours logged",
    labels={"Logged": "Logged Hours", "Key": "Task"},
    height=500,
)
fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis=dict(tickangle=45, tickmode='linear'),
    yaxis_title="Logged Hours",
    xaxis_title="Key",
)
st.plotly_chart(fig)

#-------------------------------------------------------
filtered_df = billable_df[billable_df["Logged"] < 1][["Key", "Logged"]]
st.title('Billable Tasks with Less than 1 Hour Logged')
fig = px.bar(
    filtered_df,
    x="Key",
    y="Logged",
    text="Logged",
    title="Billable tasks less than 1 hour logged",
    labels={"Logged": "Logged Hours", "Key": "Task"},
    height=500,
)
fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis=dict(tickangle=45, tickmode='linear'),
    yaxis_title="Logged Hours",
    xaxis_title="Key",
)
st.plotly_chart(fig)

#-------------------------------------------------------
filtered_df = ultilized_df[ultilized_df["Logged"] > 5][["Key", "Logged"]]
st.title('Utilized Tasks with More than 5 Hours Logged')
fig = px.bar(
    filtered_df,
    x="Key",
    y="Logged",
    text="Logged",
    title="Utilized tasks with more than 5 hours logged",
    labels={"Logged": "Logged Hours", "Key": "Task"},
    height=500,
)
fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis=dict(tickangle=45, tickmode='linear'),
    yaxis_title="Logged Hours",
    xaxis_title="Key",
)
st.plotly_chart(fig)

#-------------------------------------------------------
filtered_df = ultilized_df[ultilized_df["Logged"] < 1][["Key", "Logged"]]
st.title('Utilized Tasks with Less than 1 Hour Logged')
fig = px.bar(
    filtered_df,
    x="Key",
    y="Logged",
    text="Logged",
    title="Utilized tasks less than 1 hour logged",
    labels={"Logged": "Logged Hours", "Key": "Task"},
    height=500,
)
fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis=dict(tickangle=45, tickmode='linear'),
    yaxis_title="Logged Hours",
    xaxis_title="Key",
)
st.plotly_chart(fig)

date_columns = [date for date in df.columns if date not in ["Issue", "Key", "Logged", "Project"]]

work_data = []
for col in date_columns:
    if sum(df[col]) > 8:
        work_data.append((col, sum(df[col])))
st.markdown(f"### Số ngày làm việc hơn 8 tiếng: {len(work_data)} ngày")

less_work_data = []
for col in date_columns:
    if 0 < sum(df[col]) < 8:
        less_work_data.append((col, sum(df[col])))
st.markdown(f"### Số ngày làm việc ít hơn 8 tiếng: {len(less_work_data)} ngày")

no_work_data = []
for col in date_columns:
    if sum(df[col]) == 0:
        no_work_data.append((col, sum(df[col])))
st.markdown(f"### Số ngày nghỉ: {len(no_work_data)} ngày")

work_days = len(date_columns) - len(no_work_data)
st.markdown(f"### Tổng số ngày đi làm: {work_days} ngày")
st.markdown(f"### Tỉ lệ số ngày làm hơn 8 tiếng: {round((len(work_data) / work_days) * 100, 2)}%")

#-------------------------------------------------------
if work_data:
    st.title('Days with More than 8 Hours Logged')
    dates, values = zip(*work_data)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=values, text=values, textposition='outside'))
    fig.update_layout(
        title='Days with more than 8 hours logged',
        xaxis_title='Date',
        yaxis_title='Value',
    )
    st.plotly_chart(fig)

if less_work_data:
    st.title('Days with Less than 8 Hours Logged')
    dates, values = zip(*less_work_data)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=values, text=values, textposition='outside'))
    fig.update_layout(
        title='Days with less than 8 hours logged',
        xaxis_title='Date',
        yaxis_title='Value',
    )
    st.plotly_chart(fig)

st.markdown(f"### Trung bình log 1 ngày: {round(sum(df['Logged']) / work_days, 2)}h")
