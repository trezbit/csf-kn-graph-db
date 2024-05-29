# CSF Knowledge Graph (KG)

**Description**:  

Python and Neo4J prototoype for a Knowledge Graph, along with the basic command-line utilities for building and deploying the CSF v2.0 and v1.1 KG related associative network of relationships. Resulting KG is persisted in a Neo4J database providing:
 - Explicit mappings for Cybersecurity Standards/controls per NIST CSF v2.0 documentation and toolkits
 - Assessment questionaires and corpus segments generated by OpenAI and scoped by CSF controls
 - A network of key concepts capturing the content/semantics of CSF controls leveraging OpenAI generated core concept segments, KeyBert and PatternRank.

The goal of the prototyping effort is to seamlessly address ever evolving compliance data scope for Cybersecurity use-cases including:

- Graph based inference to effectively identify/discover derived relationships, cross-standard/control implementation dependencies extending beyond SME provided explicit mappings. 
- Capability to perform compliance and risk assessments, across standards
- Support for RAG (Retrieval-augmented-generation) in the provision of high-quality features, and embeddings for ML and Generative AI, potentially addressing shortcomings and hallucinations in large language models (LLMs).

**Status**:  Baseline version 1.0

---
### KG Model
<img src="./docs/KGModel.png" alt="drawing" width="500"/>

---

### Model Build, Processing and RAG Pipelines
<img src="./docs/Flows-graph-db.jpg" alt="drawing" width="900"/>

## Runtime Env and Dependencies
*Tested on*: Ubuntu 22.04 - *Python Version*: 3.10.12 

*Requires:* Pyhton version 3.10 or greater

Active [OpenAI API](https://platform.openai.com/) subscription allowing access to GPT 3.5+ (More on creating API keys at: [Go-OpenAI](https://github.com/sashabaranov/go-openai?tab=readme-ov-file#getting-an-openai-api-key) https://github.com/sashabaranov/go-openai?tab=readme-ov-file#getting-an-openai-api-key

Active [Neo4J - Aura](https://neo4j.com/cloud/platform/aura-graph-database/) free-tier subscription for protototype graph database access and deployment 

Optional for Inference [Langsmith](https://smith.langchain.com/) free-tier developer subscription for langchain LLM applications development platform.

## Configuration

###### ChatGPT API Connectivity

The utility expects the following environment variables to be set:

```bash
export NEO4J_URI=<YOUR_AURADB_URI>
export NEO4J_USER='neo4j'
export NEO4J_PASSWORD=<YOUR_AURADB_PWD>

export OPEN_API_SECRET=<YOUR_OPEN_API_SECRET>
```

###### Graph Build Settings

Sample keyBERT configuration is available at: `./config/keybert.json`
For graph model and CSV/JSON extraction paths, constants and enumerations, refer to `./config/includes.py`


## Usage

+ Model build 
+ KeyPhrase extraction 
+ Neo4J Access
+ Inference + RAG demo

> Node properties:
>
> STANDARD {id: INTEGER, name: STRING, display_name: STRING, role: STRING}
>
> CONTROL {id: INTEGER, name: STRING, functional_category: STRING}
>
> KEYCONCEPT {id: INTEGER, name: STRING, accronym: STRING}
>
> QUESTION {id: INTEGER, name: STRING, scope: STRING, rationale: STRING, aqtext_embedding: LIST}
>
> Relationship properties:
>
> CAPTURES {from_id: INTEGER, to_id: INTEGER, confidence: FLOAT}
>
> ASSESSES {from_id: INTEGER, to_id: INTEGER, strength: BOOLEAN}
>
> The relationships:
>
> (:STANDARD)-[:HAS_CONTROL]->(:CONTROL)
>
> (:CONTROL)-[:CAPTURES]->(:KEYCONCEPT)
>
> (:CONTROL)-[:MAPS_TO]->(:CONTROL)
>
> (:QUESTION)-[:ASSESSES]->(:CONTROL)
 

## Testing

[TODO] Rudimentary testing to be provided via `PyTest`

## Features to Implement & Known issues

- Baseline testing for `NEO4JConnector`, `GraphProcessor`, and `KeyTermExtractor` classes
- Inference Module to be added demonstrating RAG via LangChain+OpenAI Embeddings
- Dockerized version for the CLI
- Neo4J GIST submission

## Getting help

If you have questions, concerns, bug reports, etc, please file an issue in this repository's Issue Tracker.

## Open source licensing info
1. [LICENSE](LICENSE)

----
## Credits and references

#### [CSF Tools](https://csf.tools/) 

Exploration and Visualization Tools by NIST Cybersecurity Framework (CSF) and Privacy Framework (PF)

#### PatternRank

#### KeyBERT

#### LangChain

#### Neo4J

