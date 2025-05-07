import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os
import re
import logging
logging.basicConfig(level=logging.DEBUG)

from difflib import get_close_matches

from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_community.llms import LlamaCpp

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def describe_data(_):
    return str(st.session_state.df.describe(include='all'))

def get_column_names(_):
    return f"Available columns: {', '.join(st.session_state.df.columns)}"

def plot_xy(input_text: str):
    match = re.findall(r"plot\s+([\w\s]+?)\s+vs\s+([\w\s]+)", input_text, re.IGNORECASE)
    if not match:
        return "Please specify in format: plot Y vs X"

    y_raw, x_raw = match[0]
    col_map = {col.lower().replace(" ", ""): col for col in st.session_state.df.columns}

    def resolve(col_name):
        key = col_name.strip().lower().replace(" ", "")
        matches = get_close_matches(key, col_map.keys(), n=1, cutoff=0.6)
        return col_map[matches[0]] if matches else None

    x_col = resolve(x_raw)
    y_col = resolve(y_raw)

    if not x_col or not y_col:
        return f"Invalid columns. Available: {', '.join(st.session_state.df.columns)}"

    fig, ax = plt.subplots(figsize=(8, 4))
    st.session_state.df.plot(x=x_col, y=y_col, kind='line', title=f"{y_col} vs {x_col}", ax=ax)
    st.pyplot(fig)
    return f"Displayed: {y_col} vs {x_col}"

def query_average(question: str):
    match = re.search(r"average.*?(l\d)", question.lower())
    if match:
        segment = match.group(1).upper()
        if segment in st.session_state.df['Segment'].unique():
            val = st.session_state.df[st.session_state.df['Segment'] == segment]['Load'].mean()
            return f"The average load at {segment} is {val:.2f}"
    return "I couldn't parse your average query."

def query_average_age_by_sex(question: str):
    df = st.session_state.df
    match = re.search(r"average\s+age\s+of\s+(male|female)", question.lower())
    if not match:
        return "Please ask like: average age of female"

    sex = match.group(1).capitalize()
    sex_col = next((col for col in df.columns if 'sex' in col.lower()), None)
    age_col = next((col for col in df.columns if 'age' in col.lower()), None)

    if not sex_col or not age_col:
        return f"Dataset must contain 'Sex' and 'Age' columns. Found: {', '.join(df.columns)}"

    try:
        avg_age = df[df[sex_col] == sex][age_col].mean()
        return f"The average age of {sex.lower()} patients is {avg_age:.2f}"
    except Exception as e:
        return f"Error computing average age: {e}"

tools = [
    Tool(name="DescribeData", func=describe_data, description="Summarize CSV structure and stats"),
    Tool(name="GetColumns", func=get_column_names, description="List all columns in the dataset"),
    Tool(name="PlotXY", func=plot_xy, description="Plot data using 'plot Y vs X' format"),
    Tool(name="QueryAverageLoad", func=query_average, description="Answer questions about average L4L5 load"),
    Tool(name="QueryAverageAgeBySex", func=query_average_age_by_sex, description="Answer questions like 'average age of female patients'"),
]

system_prompt=(
    "You are a data analysis assistant. "
    "You have access to tools. Always follow this format:\n\n"
    "Thought: <your reasoning>\n"
    "Action: <tool name from tool list>\n"
    "Action Input: <string or '_' if not needed>\n"
    "Observation: <result from the tool>\n"
)

@st.cache_resource
def get_llm():
    return LlamaCpp(
        model_path="./models/openhermes.gguf",
        temperature=0.6,
        max_tokens=512,
        n_ctx=2048,
        verbose=False,
        system_prompt=system_prompt,
    )

@st.cache_resource
def get_agent():
    return initialize_agent(
        tools=tools,
        llm=get_llm(),
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        early_stopping_method="generate",
    )

st.title("CSV Chat Assistant with LLM + Plotting")

csv_file = st.file_uploader("Upload your CSV file", type="csv")
if csv_file:
    st.session_state.df = pd.read_csv(csv_file)
    st.success("CSV loaded. Ask a question below!")

    user_query = st.text_input("Ask a question about your data:")
    if user_query:
        agent = get_agent()
        with st.spinner("Thinking..."):
            try:
                result = agent.invoke({"input": user_query})
                st.write("Agent Result:")
                st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Upload a CSV to begin.")
