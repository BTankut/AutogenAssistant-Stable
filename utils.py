import pandas as pd
import plotly.express as px
import streamlit as st

def format_conversation(messages: list) -> str:
    """Format conversation for display"""
    formatted = ""
    for msg in messages:
        role = msg["role"].capitalize()
        content = msg["content"]
        formatted += f"**{role}**: {content}\n\n"
    return formatted

def create_metrics_charts(metrics: dict):
    """Create visualization charts for metrics"""
    # Response time chart
    if metrics['response_times']:
        df_times = pd.DataFrame({
            'Response Time (s)': metrics['response_times']
        })
        fig_times = px.line(df_times, title='Response Times')
        st.plotly_chart(fig_times)

    # Model usage chart
    if metrics['model_usage']:
        df_usage = pd.DataFrame({
            'Model': list(metrics['model_usage'].keys()),
            'Usage Count': list(metrics['model_usage'].values())
        })
        fig_usage = px.bar(df_usage, x='Model', y='Usage Count', 
                          title='Model Usage Distribution')
        st.plotly_chart(fig_usage)

def update_metrics(metrics: dict, response: dict, model: str):
    """Update metrics with new response data"""
    if response['success']:
        metrics['total_tokens'] += response['tokens']
        metrics['response_times'].append(response['time'])
        metrics['model_usage'][model] = metrics['model_usage'].get(model, 0) + 1
