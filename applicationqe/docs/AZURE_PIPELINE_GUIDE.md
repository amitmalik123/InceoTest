# Azure Pipeline Structure Guide

## Purpose

This repository uses a team-aligned pipeline model so each team can run and release independently.
The structure is based on existing team boundaries in `data`, `config`, `tests/features`, `tests/steps`, `pages`, and `queries`.

## Pipeline Files

- Root orchestrator: `azurePipeline.yaml`
- Shared template: `azure-pipelines/templates/team-stage.yml`
- Team pipelines:
	- `azure-pipelines/baw.yml`
	- `azure-pipelines/naw.yml`
	- `azure-pipelines/oam.yml`
	- `azure-pipelines/proposal.yml`
	- `azure-pipelines/model-management.yml`
	- `azure-pipelines/stp-ict.yml`
	- `azure-pipelines/stp-journals.yml`

## Trigger Strategy

Each team pipeline uses path filters so only team-relevant changes trigger runs.

Examples:
- BAW pipeline triggers on `data/BAW/**`, `tests/features/BAW/**`, and related team paths.
- Model Management pipeline triggers on `data/Model Management/**`, `tests/features/Model Management/**`, and related team paths.
- STP is split into two independent pipelines:
	- STP-ICT
	- STP-JOURNALS

## Root Pipeline Behavior

`azurePipeline.yaml` is the umbrella full-regression pipeline and runs all team stages.
Use it when validating broad changes that may affect multiple teams.

## Azure DevOps Setup

Create one pipeline entry per YAML file in Azure DevOps:

1. New pipeline -> Existing Azure Pipelines YAML file.
2. Select one file under `azure-pipelines/`.
3. Name pipeline by team (for example, `QE-BAW`, `QE-STP-ICT`).
4. Repeat for all team files.
5. Optionally create one extra entry for `azurePipeline.yaml` as `QE-Full-Regression`.

## Change Management Rules

1. Add team-specific trigger paths when a new team folder is introduced.
2. Keep common execution logic in `azure-pipelines/templates/team-stage.yml`.
3. Avoid duplicating test logic across team YAML files.
4. Keep shared dependency management in `requirements.txt` unless team dependencies diverge.

## Future Enhancements

1. Add multi-environment stages (test11, test12, silo, qa, prod) inside template with approvals.
2. Add publishing of JUnit, Allure, and coverage artifacts per team.
3. Add scheduled nightly full-regression run via `azurePipeline.yaml`.
