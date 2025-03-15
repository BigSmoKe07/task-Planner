## Task Planner 
> Task planner is a handy tool that helps you manage your tasks and boost your productivity. This tutorial uses LangChain and LangGraph to create a simple, organized process for this. It includes:

- context breakdown & analysis
- external resource retrieval (web search)
- discretization of information

## Motivation

> Let’s talk about a challenge many of us face—procrastination and messy workflows, especially for college students or folks working in non-admin roles. It happens a lot because tasks can feel unclear, and that confusion can slow us down. Imagine a software engineer at a startup tasked with building a sign-in page for a web app. They might get stuck wondering, “Should I start with the auth server or the front end?” Those questions can snowball into even more doubts, making the task feel overwhelming and pushing them to put it off. This happens everywhere, across all kinds of jobs!

That’s where this project comes in—to help you tackle tasks with confidence! task-planner uses smart AI to break down your tasks, organize them, and figure out the best way to get them done. It even looks at how you naturally like to work and tailors suggestions to fit your style. Our goal? To give you a clear, easy-to-follow plan that beats procrastination and keeps you motivated. Let’s turn those tricky tasks into wins together!

## Core

 - Data Ingestion: Gathers data for approach analysis
 - State Graph: Orchestrates steps from analysis to personalized generation
 - Tavily Web Query: Searches for information on the task to maximize task proficiency
 - LLM Model: Generates plans and analyzes approach

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run main.py
```

## License

MIT
