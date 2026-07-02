# Project Implementation Plan: Web-Based ADR Detection and Drug Recommendation System

## 1. Project Scope

The project will develop a hybrid ADR (Adverse Drug Reaction) detection system featuring two detection paths:

- **Path A (Rule/DB-based)**: Checks known drug-drug interactions (DDIs) and drug-condition contraindications against a curated database.
- **Path B (NLP-based)**: Extracts symptoms from free-text user input using NLP and matches them against known ADR profiles for a drug.
- **Recommendation Engine**: Suggests safer drug alternatives when a risk is detected.

## 2. Architecture

- **Framework**: Django (MTV pattern).
- **Structure**: Single Django codebase.
- **Database**: PostgreSQL (via Django ORM).
- **Frontend**: Django templates + Bootstrap 5.

## 3. Data Sources

- **SIDER**: Drug–side effect associations.
- **DrugBank**: Drug info, DDIs, mechanisms, ATC codes.
- **FAERS**: Real-world adverse event reports (use sparingly).
- **MedDRA**: Standard terminology for symptoms/ADRs.
- **RxNorm**: Normalizes drug names.
  *Note: Focus on a subset of 50-100 drugs (e.g., cardiovascular, diabetes, antibiotics).*

## 4. App Breakdown

- **`drugs`**: Data foundation (`Drug`, `AdverseReaction`, `DrugInteraction` models).
- **`accounts`**: User authentication (`patient`/`clinician` roles).
- **`detection`**: Service modules for `ddi_checker.py` and `nlp_extractor.py` (using scispaCy).
- **`recommender`**: Logic for suggesting safer alternatives based on rule-based scoring.

## 5. Data Loading Strategy

- Use **Django management commands** to import CSV data (SIDER/DrugBank).
- Use **Django admin** for data management and browsing.

## 6. NLP Integration

- Use **scispaCy** (e.g., `en_ner_bc5cdr_md`).
- Load the model once at startup (module-level singleton) to optimize performance.

## 7. Evaluation Plan

- **DDI engine**: Precision/recall against a held-out test set.
- **NLP extraction**: F1 score against a manually labeled sample.
- **Recommendations**: Qualitative review by a clinician/pharmacy student.

