# Watchgate

**Watchgate** is a data reliability and governance tool designed to monitor the health of data pipelines on Databricks. It tracks file arrivals, validates pipeline execution against expected schedules, detects missed deadlines, and raises tiered alarms when issues are detected.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
  - [Project Configuration (`pyproject.toml`)](#project-configuration-pyprojecttoml)
  - [Environment Variables](#environment-variables)
  - [Configuration Table Schema](#configuration-table-schema)
- [Getting Started](#getting-started)
- [Alarm Logic](#alarm-logic)
- [Alarm Output Schema](#alarm-output-schema)
- [Roadmap](#roadmap)

## Overview

Watchgate continuously checks whether expected files have landed in their designated storage locations, in line with each use case's defined frequency and deadline rules. When a file is missing or a deadline is approaching/breached, Watchgate raises an alarm with the appropriate severity level and logs the event for tracking and governance reporting.

## Features

- File existence monitoring across configurable storage paths (e.g., ADLS Gen2, SFTP-sourced areas)
- Pipeline execution tracking against expected run schedules
- Deadline detection with configurable rules (daily, weekly, monthly)
- Three-tier alarm system (early warning, deadline window, breach)
- Centralized configuration via Databricks tables
- Alarm history logging for auditing and governance

## Architecture

> _Add a brief description or diagram of the overall architecture here, e.g.:_
> - **Orchestrator notebook** — entry point that runs the monitoring checks
> - **Utils notebook** — shared functions, configuration loaders, and helpers
> - **Configuration table** — defines monitored use cases and their rules
> - **Alarm table** — stores generated alarms for downstream consumption
> - **Data Factory pipeline(s)** — schedules and triggers the monitoring runs

## Prerequisites

- A Databricks workspace with access to ADLS Gen2 (or relevant storage)
- An Azure Data Factory instance (if scheduling via ADF)
- Python 3.x
- [uv](https://github.com/astral-sh/uv) (recommended package manager for local development)

## Configuration

### Project Configuration (`pyproject.toml`)

Update `pyproject.toml` with the paths to your Databricks notebooks:

```toml
main_file = "Main_file_path"   # Orchestrator notebook
utils_file = "utils_file_path" # Helper notebook (functions, configs)
```

By default, Watchgate uses the `monitoring` schema. To use a different schema, update the schema name and define the target tables:

```toml
[tables]
_CONFIG_TABLE = "your_config_table_name"
_ALARM_TABLE  = "your_alarm_table_name"
```

### Environment Variables

Create a `.env` file at the project root with the credentials required to access Azure Data Factory:

```env
subscription_id = ''
# This program creates this resource group. If it's an existing resource group, comment out the code that creates the resource group
resource_group = ''
# The data factory name. 
factory_name = '''
```

> _Replace the variable names above with the actual variables your project expects._

### Configuration Table Schema

The `_CONFIG_TABLE` defines each monitored use case and its rules. Populate it according to the following schema:

| Column            | Type      | Description |
|-------------------|-----------|-------------|
| `_name`           | `STRING`  | Unique identifier for the use case |
| `frequency`       | `STRING`  | Expected delivery frequency (e.g., `daily`, `weekly`, `monthly`) |
| `lag_days`        | `INT`     | Number of days of tolerance before triggering an alarm |
| `deadline_rule`   | `INT`     | Deadline reference: `NULL` = daily, `0–6` = weekday, `1–31` = day of month |
| `date_mask`       | `STRING`  | Date format expected in the filename (`yyyyMMdd`, `yyyyMM`, `yyyy`, `MMdd`) |
| `length_of_date`  | `INT`     | Length of the date portion in the filename |
| `file_frequency`  | `STRING`  | Expected frequency of file delivery |
| `file_ownership`  | `BOOLEAN` | Indicates whether Watchgate owns/manages the file |
| `sender_type`     | `STRING`  | Source/sender type (e.g., SFTP, internal pipeline) |
| `sftp_area_path`  | `STRING`  | SFTP landing path (if applicable) |
| `raw_data_path`   | `STRING`  | **Required.** Path to the raw data landing zone |
| `pipeline_name`   | `STRING`  | Name of the associated pipeline |
| `subdirectory`    | `STRING`  | Subdirectory under the raw data path (`""` for flat layouts) |
| `file_template`   | `STRING`  | **Required.** Filename pattern to match (one pattern per row) |
| `updated_at`      | `TIMESTAMP` | Defaults to `current_timestamp()` |

```sql
CREATE TABLE monitoring.<config_table> (
    _name           STRING,
    frequency       STRING,
    lag_days        INT,
    deadline_rule   INT,          -- NULL = daily | weekday 0-6 | day-of-month 1-31
    date_mask       STRING,       -- yyyyMMdd | yyyyMM | yyyy | MMdd
    length_of_date  INT,
    file_frequency  STRING,
    file_ownership  BOOLEAN,
    sender_type     STRING,
    sftp_area_path  STRING,
    raw_data_path   STRING NOT NULL,
    pipeline_name   STRING,
    subdirectory    STRING,       -- "" for flat layout
    file_template   STRING NOT NULL, -- single pattern per row
    updated_at      TIMESTAMP DEFAULT current_timestamp()
);
```

## Getting Started

1. **Install dependencies**

   For local development, [uv](https://github.com/astral-sh/uv) is recommended for its speed and simplified project management:

   ```shell
   uv init
   ```

2. **Configure the project**

   - Update `pyproject.toml` as described in [Project Configuration](#project-configuration-pyprojecttoml)
   - Populate your `.env` file as described in [Environment Variables](#environment-variables)
   - Create and populate the configuration table per the [Configuration Table Schema](#configuration-table-schema)

3. **Run the monitoring tool**

   ```shell
   uv run src\notebooks\monitoring_tool.ipynb
   ```

## Alarm Logic

Watchgate evaluates each use case daily and assigns one of three alarm levels based on the current date relative to the expected run date and deadline:

| Level | Condition | Message |
|-------|-----------|---------|
| **Alarm 1 — Pending** | Current date is earlier than the next expected run date | File is missing, but there are still _n_ days remaining before the file is expected |
| **Alarm 2 — Awaiting Deadline** | Current date is between the expected run date and the deadline | File is missing and the use case is currently within its deadline window |
| **Alarm 3 — Breached** | Current date is past the deadline | File is missing and the use case should already have been executed |

## Alarm Output Schema

For each detected issue, Watchgate logs the following information to the `_ALARM_TABLE`:

| Field | Description |
|-------|-------------|
| Check Date | Date the monitoring check was performed |
| Use Case | Name/identifier of the affected use case |
| Alarm Level | Severity level (1, 2, or 3) |
| Missing File(s) | Name(s) of the missing file(s) |
| Input Path | Storage path where the file was expected |
| Input Source | Source system or sender type |
| Expected Filename | Filename pattern that was expected |
| Use Case Deadline | Deadline date for the use case |

## Roadmap

- [ ] ADF pipeline JSON generation for dynamic use case sourcing and parallel execution
- [ ] Expanded test coverage for multi-scenario edge cases
- [ ] `lag_days` validation improvements
