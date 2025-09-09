# 🤖 AI Job Autopilot - Multi-Agent Orchestration System

## Overview

The AI Job Autopilot Multi-Agent Orchestration System is a sophisticated pipeline that coordinates specialized AI agents to automate the complete job application process. The system follows the agentic architecture pattern where each agent has specific expertise and they work together through intelligent orchestration.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  📄 OCR Agent → 🔍 Parser Agent → 🧠 Skill Agent                    │
│                           ↓                                         │
│                  🎯 Discovery Agent                                  │
│                     ↓           ↓                                   │
│              🎨 UI Agent    🤖 Automation Agent                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Specifications

### 1. 📄 OCR Agent (OCRAgent)
**Purpose**: Extract text from visual documents using multiple OCR engines

**Capabilities**:
- Multi-engine OCR (Google Vision, Tesseract, EasyOCR, PaddleOCR)
- Intelligent fallback strategies
- PDF and image processing
- Quality assessment and confidence scoring

**Input**: Documents (PDF, JPG, PNG, TIFF)
**Output**: Extracted text with confidence scores

### 2. 🔍 Parser Agent (ParserAgent) 
**Purpose**: Parse resume text into structured JSON format

**Capabilities**:
- Multi-AI parsing (GPT-4o, Claude 3.5 Sonnet)
- Structured data extraction
- Field validation and cleaning
- Confidence assessment

**Input**: Extracted text from OCR Agent
**Output**: Structured resume data (JSON)

### 3. 🧠 Skill Agent (SkillAgent)
**Purpose**: Extract and analyze skills from parsed resume data

**Capabilities**:
- NLP-based skill extraction (spaCy, BERT, Transformers)
- Experience calculation per skill
- Skill strength assessment
- Soft skills identification

**Input**: Structured resume data from Parser Agent
**Output**: Skills analysis with experience and proficiency levels

### 4. 🎯 Discovery Agent (DiscoveryAgent)
**Purpose**: Find and match job opportunities

**Capabilities**:
- Multi-platform job search (LinkedIn, Indeed, Glassdoor, company sites)
- Semantic relevance scoring
- Salary estimation
- Preference-based filtering

**Input**: Candidate profile and skills analysis
**Output**: Ranked job matches with detailed analysis

### 5. 🎨 UI Agent (UIAgent)
**Purpose**: Generate modern user interface components

**Capabilities**:
- React/Vue/HTML component generation
- Glassmorphism design system
- Responsive layouts
- Dark/light mode support

**Input**: Job matches and UI specifications
**Output**: Generated UI components and code

### 6. 🤖 Automation Agent (AutomationAgent)
**Purpose**: Automate job applications with stealth mode

**Capabilities**:
- Multi-platform automation (LinkedIn, Indeed, company portals)
- Human-like behavior simulation
- Stealth mode operation
- Application tracking

**Input**: Job queue and candidate profile
**Output**: Application results and success metrics

## Pipeline Execution Flow

### Sequential Execution (Default)

1. **Document Processing**
   ```
   OCRAgent → ParserAgent → SkillAgent
   ```
   
2. **Job Discovery**
   ```
   DiscoveryAgent (uses ParserAgent + SkillAgent outputs)
   ```
   
3. **Parallel Execution** 
   ```
   UIAgent ← DiscoveryAgent → AutomationAgent
   ```

### Quality Gates

Each stage includes quality validation:
- **OCR Quality Gate**: Text extraction confidence > 70%
- **Parsing Quality Gate**: Profile completeness > 80%
- **Skill Quality Gate**: Skills identified > 5
- **Discovery Quality Gate**: Job matches found > 10
- **Automation Quality Gate**: Success rate > 80%

## Configuration

### Workflow Configuration
```python
from src.orchestration import WorkflowConfig

config = WorkflowConfig(
    workflow_id="job-automation-001",
    user_id="ankit-thakur",
    execution_mode="sequential",  # sequential, parallel, hybrid
    quality_threshold=0.8,
    max_retries=3,
    timeout_seconds=300,
    enable_stealth_mode=True,
    notification_enabled=True,
    auto_recovery=True
)
```

### Agent Configuration
```python
# OCR Agent
ocr_config = {
    'engines': ['google_vision', 'tesseract', 'easyocr', 'paddleocr'],
    'fallback_enabled': True,
    'quality_threshold': 0.7
}

# Parser Agent
parser_config = {
    'ai_models': ['gpt-4o', 'claude-3.5-sonnet'],
    'parsing_confidence_threshold': 0.8,
    'structured_output': True
}

# Discovery Agent
discovery_config = {
    'job_sources': ['linkedin', 'indeed', 'glassdoor', 'company_portals'],
    'semantic_matching': True,
    'salary_estimation': True,
    'max_jobs_per_search': 100
}
```

## Usage

### Basic Usage

```python
from src.orchestration import AIJobAutopilotOrchestrator, WorkflowConfig

# Initialize orchestrator
config = WorkflowConfig(
    workflow_id="demo-workflow",
    user_id="user123"
)
orchestrator = AIJobAutopilotOrchestrator(config)

# Prepare input
initial_input = {
    'documents': [
        {
            'document_id': 'resume-001',
            'document_type': 'resume',
            'file_path': '/path/to/resume.pdf',
            'file_format': 'pdf'
        }
    ],
    'preferences': {
        'desired_roles': ['Senior Software Engineer'],
        'preferred_locations': ['San Francisco', 'Remote'],
        'minimum_salary': 150000
    },
    'credentials': {
        'linkedin': {
            'email': 'user@example.com',
            'password': 'secure_password'
        }
    }
}

# Execute pipeline
results = await orchestrator.execute_full_pipeline(initial_input)
```

### Streamlit Integration

```python
from src.orchestration import StreamlitOrchestrationUI

# Create UI
orchestration_ui = StreamlitOrchestrationUI()
orchestration_ui.create_orchestration_page()
```

### Adding to Existing App

```python
from src.orchestration import add_orchestration_to_main_app

# Add orchestration toggle to sidebar
if add_orchestration_to_main_app():
    st.info("Multi-Agent Orchestration is now active!")
```

## API Reference

### AIJobAutopilotOrchestrator

Main orchestrator class for managing the complete workflow.

#### Methods

- `execute_full_pipeline(initial_input: Dict) -> Dict`: Execute complete pipeline
- `get_agent_status() -> Dict`: Get current agent status
- `get_workflow_state() -> Dict`: Get current workflow state

### IntegratedOrchestrator

Simplified orchestrator for demonstration and testing.

#### Methods

- `execute_pipeline(initial_input: Dict) -> Dict`: Execute simplified pipeline

### StreamlitOrchestrationUI

Streamlit interface for the orchestration system.

#### Methods

- `create_orchestration_page()`: Create main orchestration interface
- `create_agent_dashboard()`: Create agent monitoring dashboard

## Performance Metrics

### Target Performance
- **Pipeline Execution Time**: < 30 seconds for complete workflow
- **Agent Success Rate**: > 90% successful completion
- **OCR Accuracy**: > 95% text extraction accuracy
- **Job Match Relevance**: > 85% relevant matches in top 10 results
- **Application Success Rate**: > 80% successful job applications

### Monitoring
- Real-time agent status tracking
- Performance metrics collection
- Error tracking and recovery
- Quality gate validation

## Error Handling

### Retry Logic
- Exponential backoff for transient failures
- Maximum retry limits per agent
- Graceful degradation for non-critical failures

### Recovery Strategies
- **OCR Failure**: Try alternative engines, manual intervention
- **Parsing Failure**: Retry with different AI models
- **Discovery Failure**: Reduce search criteria, try alternative sources
- **Automation Failure**: Check credentials, retry with different approach

## Security & Privacy

### Data Protection
- Secure credential management
- Encrypted data transmission
- Temporary data cleanup
- No persistent storage of sensitive data

### Stealth Mode
- Human-like behavior simulation
- Browser fingerprint randomization
- Proxy rotation support
- Rate limiting compliance

## Development

### Adding New Agents

1. Extend `BaseAgent` class
2. Implement required methods
3. Add to orchestrator configuration
4. Update pipeline routing logic

### Testing

```bash
# Run unit tests
python -m pytest src/orchestration/tests/

# Run integration tests
python -m pytest src/orchestration/tests/integration/

# Run performance tests
python -m pytest src/orchestration/tests/performance/
```

### Dependencies

```
streamlit>=1.28.0
asyncio
aiohttp
openai>=1.0.0
anthropic>=0.8.0
spacy>=3.6.0
pytesseract>=0.3.10
easyocr>=1.7.0
google-cloud-vision>=3.4.0
selenium>=4.15.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
plotly>=5.17.0
```

## Roadmap

### Phase 1: Core Implementation ✅
- [x] Basic agent framework
- [x] Sequential pipeline execution
- [x] Streamlit integration
- [x] Error handling and recovery

### Phase 2: Advanced Features 🚧
- [ ] Parallel agent execution
- [ ] Advanced quality gates
- [ ] Machine learning optimization
- [ ] Performance analytics

### Phase 3: Enterprise Features 📋
- [ ] Multi-user support
- [ ] API gateway
- [ ] Advanced monitoring
- [ ] Custom agent marketplace

## Support

For issues, feature requests, or contributions:

1. Check existing issues in the repository
2. Create detailed bug reports with logs
3. Submit feature requests with use cases
4. Follow contribution guidelines for pull requests

## License

This project is part of the AI Job Autopilot system and follows the same licensing terms.

---

**Built with ❤️ for Ankit Thakur's job search automation**