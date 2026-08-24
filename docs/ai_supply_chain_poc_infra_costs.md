# Phase 8 — Infrastructure and Cost Estimates

This document summarizes a minimal infra setup for the AI Supply Chain POC and rough cost considerations.

Components:
- FastAPI backend (single small VM or dev laptop)
- Static frontend served by FastAPI
- Optional vector DB & embedding workers (Chroma + SentenceTransformers)
- Optional H2O cluster (requires Java/JRE) for AutoML
- Persistent storage: local files or S3-compatible object store for models and vectorstore

Estimated minimal monthly cost (AWS example):
- t3.small EC2 dev server: ~$20
- S3 storage (few GB): <$1
- Optional GPU instance for embeddings (on-demand): ~$0.90/hr (~$650/month if 24/7)

Recommendations:
- Use local dev for prototyping. If scaling, move vectorstore to managed DB and host models in containers.
- Track inference cost by instrumenting requests and model durations.
