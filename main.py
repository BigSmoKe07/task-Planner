import os
import re
import streamlit as st
from typing import TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tavily import TavilyClient


class ApproachState(TypedDict):
    plan: str  # detailed workflow of the approach
    style: str  # style description of the approach
    task: str  # user's input of task
    details: str  # internet retrieval of task specs
    history: str  # description of history approaches


st.title("Task Planner")
st.write("A task management app that uses LLMs to help you manage your tasks and improve your productivity.")
st.sidebar.title('Settings')
groq_api_key = st.sidebar.text_input(
    "Groq API Key", value=os.getenv("GROQ_API_KEY"), type="password")
tavily_api_key = st.sidebar.text_input(
    "Tavily API Key", value=os.getenv("TAVILY_API_KEY"), type="password")

if groq_api_key and tavily_api_key:
    st.sidebar.success("API key set successfully.")
else:
    st.sidebar.error("Please set both API keys.")


def approach_analysis(approach: ApproachState) -> ApproachState:
    """Retrieve history approach and let LLM do a qualitative analysis on user approach preference."""
    history = ""
    for h in os.listdir(f"{os.getcwd()}/history"):
        if (h[-4:] == ".txt"):
            with open(os.path.join(os.getcwd(), f"history/{h}")) as f:
                content = f.readlines()
            history = f"{history}\n{content[0]}"

    approach['history'] = history

    prompt = ChatPromptTemplate.from_template(
        "Analyze the work style the following summary of work history portrays. "
        "Provide a brief summary the preference in work style."
        "\n\nWork History: {history}"
    )
    style = llm.invoke(prompt.format(history=approach['history']))
    approach['style'] = style
    return approach


def task_manifest(approach: ApproachState) -> ApproachState:
    """use Tavily to look up information on the task."""

    search_foundation = "What are the steps for the following task? {task}"
    search_query = search_foundation.format(task=approach["task"])

    searches = tavily_client.search(search_query, max_results=10)

    details = ""

    for result in searches['results']:
        if details == "":
            details = result['content']
        else:
            details = f"{details} {result['content']}"

    approach["details"] = details

    return approach


def result_approach(approach: ApproachState) -> ApproachState:
    prompt = ChatPromptTemplate.from_template(
        "Give me a plan of steps to carry out the following task with custom work styles specified."
        "You have to pay extra attention to Work Style mentioned below and adjust the plan accordingly."
        "\n\nTask: {task}\n\nDetails: {details}\n\nWork Style: {style}\n\n"
        "The output must be a numbered list of steps with explanation of why it is needed, what to do and how it considers the Work Style."
    )

    suggestion = llm.invoke(prompt.format(
        task=approach["task"], details=approach["details"], style=approach["style"]))

    approach['plan'] = suggestion

    return approach


# Initialize the StateGraph
workflow = StateGraph(ApproachState)

# Add nodes to the graph
workflow.add_node("approach_analysis", approach_analysis)
workflow.add_node("task_knowledge_retrieval", task_manifest)
workflow.add_node("customized_approach_generation", result_approach)

# Define and add conditional edges
workflow.add_edge("approach_analysis", "task_knowledge_retrieval")
workflow.add_edge("task_knowledge_retrieval", "customized_approach_generation")
workflow.set_entry_point("approach_analysis")
workflow.add_edge("customized_approach_generation", END)

# Compile the graph
app = workflow.compile()


def approach(task: str) -> ApproachState:
    init_approach = ApproachState(
        task=task,
        plan="",
        style="",
        history="",
        details=""
    )

    response = app.invoke(init_approach)
    task_name = task[:25]
    task_name = re.sub(r'[^a-zA-Z0-9\s\-]', '', task).replace(' ', '-')
    filename = os.path.join(os.getcwd(), "history", f"{task_name}-history.txt")
    counter = 1
    while os.path.exists(filename):
        filename = os.path.join(
            os.getcwd(), f"{task_name}-history-{counter}.txt")
        counter += 1

    # Save the task to history
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(task)
    except Exception as e:
        st.error(f"Failed to save task to history: {e}")
    return response


message = st.chat_message("assistant")
prompt = st.chat_input("What is your task?")
if prompt:
    if not groq_api_key or not tavily_api_key:
        st.error("Please set both API keys.")
    else:
        # Initialize the Groq model
        llm = ChatGroq(api_key=groq_api_key, model="llama-3.3-70b-versatile")
        tavily_client = TavilyClient(api_key=tavily_api_key)

        generated_plan = approach(task=prompt)
        message = st.chat_message("assistant")
        message.write(generated_plan['plan'].content)
