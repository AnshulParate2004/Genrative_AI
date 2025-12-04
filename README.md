# 🤖 My Generative AI Learning Journey

Welcome to my comprehensive Generative AI learning repository! This collection represents my hands-on exploration of cutting-edge AI technologies, from foundational concepts to advanced agentic systems.

---

## 📚 Table of Contents

1. [LangChain Fundamentals](#-langchain-fundamentals)
2. [LangGraph & State Management](#-langgraph--state-management)
3. [AI Agents (Without LangChain)](#-ai-agents-without-langchain)
4. [Deep Concepts](#-deep-concepts)
5. [MCP Server Development](#-mcp-server-development)
6. [Key Technologies Used](#-key-technologies-used)

---

## 🔗 LangChain Fundamentals

### Basic Concepts
I started my journey by mastering LangChain's core components and building blocks.

#### **Message Handling & Model Integration**
- **`learn0.py`** - Dual LLM setup comparing Google Gemini 2.5 Pro and Groq Llama-3.3-70B responses
- **`learn1.py`** - Interactive chatbot with alternating model responses and persistent chat history
- **`template_messages.py`** - Dynamic prompt templating with system and human messages

#### **Chain Building Progression**
1. **`chain1.py`** - Simple LCEL chain with prompt template → model → string parser
2. **`chain2.py`** - Explicit RunnableSequence implementation showing chain internals
3. **`chain3.py`** - Multi-stage translation chain (facts → English → French)
4. **`chain4_parallel.py`** - Parallel execution with movie analysis (plot & characters simultaneously)
5. **`chain5_conditional.py`** - Branching logic for sentiment-based feedback routing
6. **`chain6_pydantic.py`** - Structured output using Pydantic models for movie analysis

### Advanced Features

#### **Agents**
- **`agent.py`** - ReAct agent with custom tool (system time) using LangChain Hub prompts

#### **RAG (Retrieval Augmented Generation)**
- **`rag.py`** - Complete RAG pipeline with ChromaDB vector store and similarity search
- **`common_embeder.py`** & **`common_searchvdb.py`** - Reusable embedding and search utilities
- **`metadata_embeder.py`** & **`metadata_search.py`** - Enhanced RAG with metadata filtering
- **`basic_react_agent.py`** - ReAct agent integrated with RAG retrieval

#### **Memory & Persistence**
- **`learnfirebase.py`** - Firebase Firestore integration for persistent chat history across sessions

---

## 🕸️ LangGraph & State Management

LangGraph became my framework for building stateful, multi-agent systems with complex workflows.

### **Basic Chatbots**
- **`basic_chatbot.py`** - Foundation graph with single chatbot node
- **`chatbot_with_memory.py`** - State persistence across conversations
- **`chatbot_with_sqlite_checkpointmemory.py`** - SQLite-backed checkpointing for conversation recovery
- **`chatbot_with_tools.py`** - Tool-augmented chatbot with external capabilities

### **State Graph Fundamentals**
- **`StateGraph_Basics/`** - Core concepts of state management and graph transitions

### **ReAct Agent Implementation**
- **`react_state.py`** - State schema for agent reasoning and actions
- **`agent_reason_runable.py`** - Reasoning logic and tool invocation
- **`react_graph.py`** - Complete ReAct loop (Reason → Act → Observe) for SpaceX launch queries

### **Reflexion Systems**
Advanced self-improving agents that critique and refine their outputs:

- **`Reflexion_basic_agent/`** - Basic reflexion pattern
- **`Reflexion_agent_system/`** - Production-ready reflexion architecture
  - **`schema.py`** - Type definitions for agent states
  - **`chains.py`** - First responder and revision chains
  - **`execute_tools.py`** - Tool execution layer with error handling
  - **`reflexion_graph.py`** - Complete self-critique loop with MAX_ITERATIONS control

### **Multi-Agent Systems**
My most advanced work - coordinating specialized agents:

#### **`supervisor_multiagent_workflow.py`** - Hierarchical Multi-Agent System
**Architecture:**
```
User Input → Supervisor → [Enhancer | Researcher | Coder] → Validator → [Continue | Finish]
```

**Specialized Agents:**
1. **Supervisor** - Orchestrates workflow and routes to specialists
2. **Enhancer** - Clarifies and improves user queries
3. **Researcher** - Gathers information using Tavily search
4. **Coder** - Executes technical tasks with Python REPL
5. **Validator** - Quality checks and completion detection

**Key Features:**
- Dynamic routing based on task requirements
- Structured outputs with Pydantic validation
- Graceful completion detection
- Tool integration (Tavily Search, Python REPL)

#### **Other Multi-Agent Work**
- **`Subgraph_Multiagent/`** - Nested graph architectures and supervisor patterns
- **`Human_approval_graph/`** - Human-in-the-loop workflows
  - **`input.py`** & **`resume.py`** - Interrupt and continuation patterns
  - **`command.py`** - Explicit approval mechanisms

### **Advanced Patterns**
- **`Pydantic_outputs/`** - Type-safe structured outputs
- **`Rag/`** - RAG integrated with LangGraph state machines

---

## 🤖 AI Agents (Without LangChain)

Building agents from scratch to understand core mechanics.

### **Memory-Aware Chatbots**
- **`AIchatBot.py`** - Advanced chatbot using Mem0, Groq, and Qdrant
  - Hybrid memory (short-term + long-term with vector search)
  - Rate limit handling with backoff strategies
  - HuggingFace embeddings (sentence-transformers)
  - Qdrant vector database integration

- **`AIchatBot1.py`** & **`AIchatBot2.py`** - Iterative improvements and variations
- **`Chatbot.py`** - Minimal chatbot implementation
- **`AChat.py`** - Chat interface experiments

### **Query Solving**
- **`Query_solver.py`** - Complex query decomposition and solving

### **Mathematical Reasoning**
- **`maths/groq.py`** - Structured JSON output for step-by-step math solutions
  - Uses DeepSeek-R1-Distill-Llama-70B reasoning model
  - Saves solutions to JSON files
- **`maths/hugging.py`** - HuggingFace model integration for math
- **`mathstoken.py`** & **`tokenization.py`** - Token analysis experiments

### **Web Scraping & Automation**
- **`AutoScraper/serper.py`** - Serper API integration for search
- **`AutoScraper/SuperScraper.py`** - Advanced web scraping utilities
- **`AutoScraper/combined.py`** - Multi-source data aggregation
- **`WebAutoScraper/`** - Automated web data extraction

### **Model Integrations**
- **`Groq.py`** - Direct Groq API usage and optimization
- **`ollama_api.py`** - Local Ollama model integration
- **`langchain.py`** - LangChain API experiments

### **Specialized Systems**
- **`Langfuse/`** - LLM observability and tracing
- **`Medkit/`** - Healthcare-focused AI applications
- **`RelationDB/`** - Database interaction agents
- **`ParallelFanOut/`** & **`LLMParallelFanOut/`** - Concurrent execution patterns
- **`Lang_graph/`** - Custom graph implementations

### **Learning Materials**
- **`Gen_AI_1.ipynb`** & **`Gen_AI_2.ipynb`** - Comprehensive Jupyter notebooks with experiments
- **`node-handbook.pdf`** - Reference documentation

---

## 🧠 Deep Concepts

Advanced techniques for production-grade AI systems.

### **Text Chunking Strategies**
Explored 7 different chunking methods for optimal RAG performance:

1. **`FixedSizeChunking.py`** - Simple fixed-size splits (baseline)
2. **`CharacterTextSplitter.py`** - Character-based splitting with overlap
3. **`RecursiveCharacterTextSplitter.py`** - Hierarchical splitting (LangChain default)
4. **`SlidingWindowchunking.py`** - Overlapping windows for context preservation
5. **`SemanticChunker.py`** - Meaning-based chunking using embeddings
   - Percentile-based breakpoint detection
   - Preserves semantic coherence
6. **`HierarchicalChunking.py`** - Multi-level document structure
7. **`AgenticChunking.py`** - LLM-powered intelligent splitting

**Key Insights:**
- Semantic chunking dramatically improved RAG accuracy for Tesla financial documents
- Trade-offs between chunk size, overlap, and retrieval precision
- When to use each strategy based on document type

### **State Management**
- **`StateTransfer/`** - State passing between graph nodes and persistence patterns

### **Unstructured Data**
- **`Unstructure.io/`** - Integration with Unstructured.io for document parsing

---

## 🛠️ MCP Server Development

Building Model Context Protocol servers for extending LLM capabilities.

### **MCP_Server (Python)**
- **`MCP_File_Manager.py`** (27.8KB) - Comprehensive file operations server
  - Read, write, edit, search, and manage files
  - Support for various text encodings
  - VS Code integration
- **`MCP_Google_Auth.py`** - Google OAuth integration for MCP
- **`config.json`** - Server configuration and settings

### **MCP_Server (TypeScript)**
- **`MCP_Server(tsx)/`** - TypeScript implementation for Node.js environments

### **MCP Client**
- **`mcp-client/`** - Client implementations for testing MCP servers

---

## 🔧 Key Technologies Used

### **LLM Providers**
- **Google Gemini** (2.5 Pro, 2.5 Flash) - Primary models for experimentation
- **Groq** (Llama-3.3-70B) - Fast inference with streaming
- **DeepSeek-R1-Distill-Llama-70B** - Reasoning-optimized model
- **Ollama** - Local model deployment

### **Frameworks & Libraries**
- **LangChain** - Chain orchestration and agent building
- **LangGraph** - Stateful multi-agent workflows
- **Mem0** - Long-term memory management
- **Pydantic** - Data validation and structured outputs

### **Vector Databases & Storage**
- **ChromaDB** - Local vector storage for RAG
- **Qdrant** - Production vector database with filters
- **Firebase Firestore** - Cloud-based persistence
- **SQLite** - Lightweight checkpointing

### **Tools & APIs**
- **Tavily Search** - Web search for agents
- **Python REPL Tool** - Code execution in agents
- **Serper API** - Search engine integration
- **HuggingFace** - Model hosting and embeddings

### **Development Tools**
- **Docker Compose** - Service orchestration
- **Neo4j** - Graph database for knowledge graphs
- **VS Code** - Primary IDE with file manager integration

---

## 📊 Project Statistics

- **Total Files**: 100+ Python scripts, notebooks, and configurations
- **Lines of Code**: ~15,000+
- **Topics Covered**: 
  - Prompt Engineering
  - Chain Building (Sequential, Parallel, Conditional)
  - Agent Development (ReAct, Reflexion)
  - Multi-Agent Systems
  - RAG Pipelines
  - Memory Systems
  - State Management
  - Tool Integration
  - MCP Server Development

---

## 🎯 Key Learning Outcomes

1. **Chain Complexity Progression**: From simple LCEL chains to complex parallel and conditional workflows
2. **Agent Autonomy**: Built agents that reason, use tools, and self-correct
3. **State Management**: Mastered LangGraph for complex stateful interactions
4. **Production Patterns**: Implemented proper error handling, rate limiting, and persistence
5. **Memory Architecture**: Created hybrid memory systems combining short-term and long-term storage
6. **Multi-Agent Coordination**: Developed supervisor patterns for specialist agent orchestration
7. **RAG Optimization**: Experimented with 7 chunking strategies for optimal retrieval
8. **Custom Tools**: Extended LLM capabilities through MCP servers and custom tool integration

---

## 🚀 What's Next

- [ ] Advanced prompt optimization techniques
- [ ] Fine-tuning custom models
- [ ] Production deployment strategies
- [ ] Performance benchmarking across providers
- [ ] Building domain-specific AI applications

---

## 💡 Notable Experiments

### **Most Complex System**: Supervisor Multi-Agent Workflow
- 5 specialized agents working in harmony
- Dynamic routing based on task analysis
- Quality validation loop
- Successfully handles weather queries, math problems, and open-ended questions

### **Most Interesting Technique**: Reflexion Agent
- Self-critique and improvement loop
- Iterative refinement up to MAX_ITERATIONS
- Demonstrates meta-learning capabilities

### **Most Practical**: RAG with Metadata Filtering
- Enhanced retrieval accuracy with source metadata
- Production-ready error handling
- Efficient vector similarity search

---

## 📝 Notes

This repository represents my journey from LangChain basics to building sophisticated multi-agent systems. Each file contains working code with detailed comments explaining the concepts. The progression shows evolution from simple chains to complex orchestration systems.

Feel free to explore, learn, and build upon these examples!

---

**Last Updated**: December 2024  
**Status**: Actively Learning 🚀