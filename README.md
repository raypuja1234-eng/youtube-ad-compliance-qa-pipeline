# YouTube Ad Compliance QA Pipeline

An AI-powered compliance auditing pipeline for YouTube video ads. The system downloads a YouTube video, extracts transcript and on-screen text via Azure Video Indexer, retrieves relevant brand and regulatory rules from Azure AI Search, and uses a LangGraph workflow with Azure OpenAI to detect policy violations and generate a compliance report.

## Overview

This repository implements a full-stack Python prototype for automated brand and advertising compliance QA. It is designed around a retrieval-augmented generation (RAG) workflow that combines:

- YouTube video ingestion
- Azure Video Indexer for analysis
- Azure AI Search for compliance rule retrieval
- Azure OpenAI for reasoning and violation detection
- LangGraph for orchestration
- FastAPI for exposing an API

The result is a reusable pipeline that can evaluate whether a promotional video includes issues such as misleading claims, prohibited statements, banned regulatory language, or broken brand guidance.

## Project goals

- Audit a YouTube ad automatically against stored compliance rules
- Extract speech and OCR content from video assets
- Retrieve relevant policy documents from a vector knowledge base
- Produce a final PASS/FAIL compliance assessment with a human-readable summary
- Expose the workflow through an API for integration into a broader QA system

## Architecture

The application follows a simple agentic workflow:

1. A video URL is submitted.
2. The system downloads the video.
3. The video is uploaded to Azure Video Indexer for transcription and OCR.
4. The extracted transcript and text are passed to the compliance agent.
5. Relevant PDF policy documents are indexed in Azure AI Search.
6. The LLM compares video content with retrieved rules and flags violations.
7. A final report is returned as structured results and summary text.

## Repository structure

```text
.
├── .gitignore
├── .python-version
├── README.md
├── main.py
├── pyproject.toml
├── uv.lock
├── backend
│   ├── data
│   │   ├── 1001a-influencer-guide-508_1.pdf
│   │   └── youtube-ad-specs.pdf
│   ├── scripts
│   │   └── index_documents.py
│   └── src
│       ├── api
│       │   ├── server.py
│       │   └── telemetry.py
│       ├── graph
│       │   ├── __init__.py
│       │   ├── nodes.py
│       │   ├── state.py
│       │   └── workflow.py
│       └── services
│           └── video_indexer.py
└──
```

## Key components

### 1. Main entry point

- `main.py`
- Starts a simulated audit run using a sample YouTube URL.
- Builds the initial workflow state and prints the final compliance report.

### 2. Workflow orchestration

- `backend/src/graph/workflow.py`
- Uses `langgraph.StateGraph` to connect the indexer and auditor nodes.
- Defines the execution path:
  - `indexer -> auditor -> END`

### 3. State schema

- `backend/src/graph/state.py`
- Defines the graph state used throughout the workflow.
- Includes video metadata, transcript, OCR text, compliance findings, final status, and errors.

### 4. Video ingestion and analysis

- `backend/src/services/video_indexer.py`
- Downloads YouTube videos using `yt-dlp`.
- Authenticates with Azure and requests an access token for Azure Video Indexer.
- Uploads the video for processing.
- Polls for processing status.
- Extracts transcript and OCR content for compliance evaluation.

### 5. Compliance reasoning

- `backend/src/graph/nodes.py`
- Contains the `index_video_node` and `audit_content_node` nodes.
- Uses Azure OpenAI to assess content against retrieved rules.
- Uses Azure AI Search to fetch the most relevant policy documents.
- Returns structured JSON with violations, status, and final summary.

### 6. Knowledge indexer

- `backend/scripts/index_documents.py`
- Loads PDF regulations and guidance documents from `backend/data`.
- Splits the text into chunks.
- Creates embeddings with Azure OpenAI.
- Uploads the chunks into Azure AI Search.

### 7. API server

- `backend/src/api/server.py`
- Exposes a FastAPI app with:
  - `POST /audit` for submitting a video URL
  - `GET /health` for service health checks
- Validates incoming request payloads with Pydantic models.

### 8. Telemetry

- `backend/src/api/telemetry.py`
- Configures Azure Monitor/OpenTelemetry when an Application Insights connection string is available.
- Enables observability and request monitoring for the API service.

## Data and knowledge base

The repository includes reference PDF documents under `backend/data`:

- `youtube-ad-specs.pdf`
- `1001a-influencer-guide-508_1.pdf`

These files are intended to serve as the policy and compliance knowledge base used by the RAG system. They are indexed into Azure AI Search so the model can retrieve the most relevant rules while evaluating ad content.

## Tech stack

- Python 3.13
- FastAPI
- LangGraph
- LangChain
- Azure OpenAI
- Azure AI Search
- Azure Video Indexer
- Azure Monitor OpenTelemetry
- PyPDF
- yt-dlp
- Pydantic
- Python-dotenv

## Environment variables

Create a `.env` file in the project root with the following configuration values, depending on your Azure setup:

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_CHAT_DEPLOYMENT=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=

AZURE_VI_ACCOUNT_ID=
AZURE_VI_LOCATION=
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=
AZURE_VI_NAME=brand-yt-project-11

APPLICATIONINSIGHTS_CONNECTION_STRING=
```

Notes:
- Azure OpenAI and Azure AI Search are required for the retrieval and analysis pipeline.
- Azure Video Indexer credentials are required for the download/upload/indexing flow.
- Application Insights is optional but enables telemetry.

## Setup

### Option 1: uv

```bash
uv sync
```

### Option 2: pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you are using the project as configured in `pyproject.toml`, prefer installing dependencies with `uv` or `pip install` for the required packages listed there.

## Run the workflow

### Simulated CLI audit

```bash
python main.py
```

This runs the sample workflow defined in `main.py` against a default YouTube URL.

### Start the API server

```bash
uvicorn backend.src.api.server:app --reload
```

Then call the audit endpoint:

```bash
curl -X POST http://127.0.0.1:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://youtu.be/dT7S75eYhcQ"}'
```

### Index the compliance PDFs

```bash
python backend/scripts/index_documents.py
```

This script loads the PDF rule documents from `backend/data`, splits them into chunks, and stores them in Azure AI Search for semantic retrieval.

## Example workflow behavior

The system is built to return results in a structured form similar to:

```json
{
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "The ad makes a claim that appears to be unsupported by the evidence presented in the video."
    }
  ],
  "status": "FAIL",
  "final_report": "The ad contains a potentially misleading claim and should be reviewed before publication."
}
```

## Use cases

This project is useful for:

- Brand review automation
- Advertising compliance QA
- Influencer campaign review
- Regulatory content monitoring
- Video content policy enforcement for marketing teams

## Limitations and considerations

- Azure services must be provisioned and configured correctly.
- The system currently expects YouTube URLs and may fail if the source video is unavailable or restricted.
- Video indexing is asynchronous and may require waiting for processing completion.
- The project is a prototype and may need environment-specific tuning for production deployments.
- Success depends on access to a valid Azure OpenAI deployment, Azure AI Search index, and Azure Video Indexer account.

## Summary

This repository is a Python-based AI compliance pipeline for auditing YouTube advertisements. It combines modern AI, retrieval, and orchestration tools to automate the review of ad content against policy and brand requirements. The design is modular, Azure-centric, and suitable for extension into a production compliance QA workflow.

## Notes

- The repository is intentionally structured around clear modular responsibilities.
- The workflow can be extended with additional nodes, rule sources, or output formats.
- The project is best suited for experimentation, internal tooling, and proof-of-concept automation in regulated marketing environments.
