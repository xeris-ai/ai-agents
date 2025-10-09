# AI Agents - Modular Agent System

A modular system for running different AI agents with AWS Bedrock. Each agent has specialized system prompts and tools for specific use cases.

## 📁 Project Structure

```
ai-agents/
├── agents/                    # Agent modules
│   ├── __init__.py           # Agent registry and utilities
│   ├── hr_assistant.py       # HR assistant (with tools)
│   ├── financial_advisor.py  # Financial advisor (with tools)
│   ├── customer_support.py   # Customer support (with tools)
│   ├── tech_support.py       # Technical support (with tools)
│   ├── bank_advisor.py       # Bank advisor (no tools)
│   ├── travel_planner.py     # Travel planner (with tools)
│   ├── code_reviewer.py      # Code review assistant (with tools)
│   ├── devops_automation.py  # DevOps automation (with tools)
│   ├── generic_chatbot.py    # General chatbot (no tools)
│   ├── ecommerce_assistant.py      # E-commerce assistant (with tools)
│   └── healthcare_scheduler.py     # Healthcare scheduler (with tools)
├── config/                    # Configuration files
│   ├── __init__.py
│   └── bedrock_config.py     # AWS Bedrock configuration
├── main.py                    # Main runner script
└── README.md                  # This file
```

## 🤖 Available Agents

### Agents with Tools (10)

1. **HR Assistant** (`hr`) - Employee queries and HR processes
2. **Financial Advisor** (`financial`) - Investment and financial planning
3. **Customer Support** (`customer_support`) - Customer inquiries and service
4. **Technical Support** (`tech_support`) - Troubleshooting technical issues
5. **Travel Planner** (`travel`) - Trip planning and itineraries
6. **Code Review Assistant** (`code_review`) - Code quality and best practices
7. **DevOps Automation** (`devops`) - CI/CD and infrastructure
8. **E-commerce Assistant** (`ecommerce`) - Product discovery and shopping
9. **Healthcare Scheduler** (`healthcare`) - Appointment scheduling
10. **Banking Advisor** (`bank`) - Banking products and services

### Agents without Tools (3)

1. **Bank Advisor** (`bank`) - General banking information
2. **Documentation Assistant** (`documentation`) - Creating documentation
3. **Generic Chatbot** (`chatbot`) - General conversations

## 🚀 Usage

### List All Available Agents

```bash
python main.py --list
```

### Show Agent Details

```bash
python main.py --agent hr --show
python main.py --agent customer_support --show
```

### Simulate Agent with Message

```bash
python main.py --agent hr --message "How many vacation days do I have?"
python main.py --agent travel --message "Plan a trip to Japan"
```

### Export Agent Configuration

```bash
# Export to stdout
python main.py --agent financial --export

# Export to file
python main.py --agent customer_support --export customer_agent.json
```

## 📝 Agent Module Structure

Each agent module contains:

```python
# Agent metadata
AGENT_CONFIG = {
    "type": "agent",
    "categories": ["category1", "category2"],
    "has_tools": "yes" or "no",
    "name": "Agent Name",
    "description": "Short description"
}

# System prompt
SYSTEM_PROMPT = """
Complete system prompt with guidelines...
"""

# Available tools (empty list if no tools)
TOOLS = [
    "tool_name_1",
    "tool_name_2",
    ...
]
```

## 🔧 Adding New Agents

1. Create a new file in `agents/` directory:

```python
# agents/my_new_agent.py

AGENT_CONFIG = {
    "type": "agent",
    "categories": ["category1", "category2"],
    "has_tools": "yes",
    "name": "My New Agent",
    "description": "Agent description"
}

SYSTEM_PROMPT = """
Your system prompt here...
"""

TOOLS = [
    "tool1",
    "tool2"
]
```

2. Register the agent in `agents/__init__.py`:

```python
from . import my_new_agent

AVAILABLE_AGENTS = {
    # ... existing agents
    "mynew": my_new_agent
}
```

## 🌐 AWS Bedrock Integration

The project includes a configuration template for AWS Bedrock integration in `config/bedrock_config.py`.

To use with AWS Bedrock:

1. Install boto3:
```bash
pip install boto3
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Update `config/bedrock_config.py` with your Bedrock configuration

4. Implement the `invoke_bedrock_agent()` function to call AWS Bedrock

## 📊 Agent Categories

Each agent is tagged with categories for classification:

- **HR & Employee**: HR, human resources, employee assistant
- **Financial**: financial advisor, finance, investment, banking
- **Support**: customer support, technical support, IT support
- **Development**: code review, software development, DevOps
- **Travel & Lifestyle**: travel planner, trip planning, tourism
- **E-commerce**: shopping assistant, retail
- **Healthcare**: appointment scheduling, medical assistant
- **Documentation**: technical writing, content creation
- **General**: chatbot, conversational AI, assistant

## 🛡️ Security Guidelines

All agents follow security best practices:

- Never disclose internal tools or systems
- Never assume parameter values
- Request missing information from users
- Maintain professional and helpful tone
- Follow role-specific compliance requirements (HIPAA, financial regulations, etc.)

## 📋 Examples

### Example 1: Check HR Agent

```bash
$ python main.py --agent hr --show

======================================================================
AGENT: HR Assistant
======================================================================

Description: Professional HR assistant for employee queries and HR processes
Categories: HR, human resources, employee assistant
Has Tools: yes

Available Tools (5):
  - check_pto_balance
  - submit_leave_request
  - view_company_policies
  - access_employee_handbook
  - check_benefits_enrollment

----------------------------------------------------------------------
SYSTEM PROMPT:
----------------------------------------------------------------------
[Full system prompt displayed...]
======================================================================
```

### Example 2: Simulate Customer Support

```bash
$ python main.py --agent customer_support --message "I need to return an item"

======================================================================
SIMULATING: Customer Support
======================================================================

User Message: I need to return an item

[NOTE: This is a simulation. In production, this would call AWS Bedrock]

Agent Configuration:
  - System Prompt: Loaded (1234 chars)
  - Tools Available: 5
  - Tool List: check_warranty_status, view_customer_profile, get_order_history, process_return_refund, search_knowledge_base

======================================================================
```

### Example 3: Export Agent Config

```bash
$ python main.py --agent financial --export financial_agent.json
Agent configuration exported to: financial_agent.json
```

## 🤝 Contributing

To add new agents or modify existing ones:

1. Follow the agent module structure
2. Include appropriate security guidelines
3. Specify tools clearly (or empty list if no tools)
4. Add clear categories for classification
5. Register in `agents/__init__.py`

## 📄 License

This project is a template for building AI agent systems with AWS Bedrock.

## 🔗 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
