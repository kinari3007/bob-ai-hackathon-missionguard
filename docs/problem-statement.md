# Problem Statement

## Background

Problem D1 of the IBM BoB AI Innovation Hackathon 2026 asks for a **Mission Readiness & Predictive Maintenance Copilot**. Fleets of vehicles, generators, and related assets produce sensor-like and service-history fields. Leaders still have to translate those fields into “can this asset go?” and “what should we fix first?”

This prototype uses **fictional** data only.

## The Problem

Operators can store temperatures, vibration, hours, and last-service dates, yet still lack a consistent, explainable ranking of mission readiness and near-term failure risk. Manual review does not scale when many assets must be compared quickly.

## Who is Affected

Mission planners and maintainers who must decide grounding vs. fly/drive/run decisions using incomplete, spreadsheet-style evidence (in this repo: a synthetic stand-in for that evidence).

## Why It Matters

Sending a degraded asset increases disruption; over-grounding a healthy one wastes availability. A transparent score with factors and a next action is the minimum useful decision aid.

## Why Existing Solutions Fall Short

Generic dashboards show raw telemetry without a documented readiness rule. Black-box models that omit “why” are a poor fit for a copilot that must justify maintenance priority. This phase therefore prefers an interpretable hybrid model over deep learning.
