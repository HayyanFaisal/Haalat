"""Task definitions for Haalat's sequential emergency workflow."""
from __future__ import annotations
from crewai import Task
from agents import (
    emergency_classifier_agent,
    language_router_agent,
    resource_locator_agent,
)

language_detection_task = Task(
    description=(
        "Inspect the incoming user input: {user_input}\n\n"
        "Detect the source language: Urdu, Sindhi, Pashto, English, or Mixed/Unknown. "
        "Force downstream tasks to output user-facing response in this language."
    ),
    expected_output=(
        "A JSON block only:\n"
        "{\n"
        '  "detected_language": "Urdu|Sindhi|Pashto|English|Mixed/Unknown",\n'
        '  "input_type": "audio|text"\n'
        "}"
    ),
    agent=language_router_agent,
)

classification_task = Task(
    description=(
        "Using input {user_input} and detected language, call emergency_rag_tool. "
        "Assign severity 1-5 and write reasoning in user's source language."
    ),
    expected_output=(
        "A JSON block only:\n"
        "{\n"
        '  "type": "emergency type",\n'
        '  "severity": 1-5,\n'
        '  "reasoning": "reasoning in source language"\n'
        "}"
    ),
    agent=emergency_classifier_agent,
    context=[language_detection_task],
)

resource_location_task = Task(
    description=(
        "Using classified emergency, location {user_location}, and detected language, "
        "call location_finder_tool. Produce final dispatch in source language."
    ),
    expected_output="Concise dispatch details containing emergency type, services, and volunteers.",
    agent=resource_locator_agent,
    context=[language_detection_task, classification_task],
)
