# Simple Usage Guide

## 🎯 Main Commands

All functionality is in one file: **`main.py`**

### List All Agents
```bash
python3 main.py --list
```

### Show Agent Details
```bash
python3 main.py --agent hr --show
```

### Chat with an Agent
```bash
python3 main.py --agent hr --message "How many vacation days do I have?"
python3 main.py --agent chatbot --message "Hello!"
python3 main.py --agent customer_support --message "I need help with my order"
```

### Export Agent Config
```bash
python3 main.py --agent financial --export config.json
```

## 📋 Setup (First Time Only)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure .env file exists with your AWS credentials
# (Already created for you!)

# 3. Test it
python3 main.py --agent chatbot --message "Hello"
```

## 🤖 Available Agents

| Agent Key | Name | Has Tools |
|-----------|------|-----------|
| `hr` | HR Assistant | ✓ |
| `financial` | Financial Advisor | ✓ |
| `customer_support` | Customer Support | ✓ |
| `tech_support` | Technical Support | ✓ |
| `bank` | Bank Advisor | ✗ |
| `travel` | Travel Planner | ✓ |
| `code_review` | Code Review Assistant | ✓ |
| `devops` | DevOps Automation | ✓ |
| `documentation` | Documentation Assistant | ✗ |
| `chatbot` | Generic Chatbot | ✗ |
| `ecommerce` | E-commerce Assistant | ✓ |
| `healthcare` | Healthcare Scheduler | ✓ |

## 📁 Project Structure

```
ai-agents/
├── main.py              ← Main script (everything you need!)
├── .env                 ← Your AWS credentials
├── agents/              ← 12 agent definitions
├── config/              ← AWS Bedrock configuration
└── requirements.txt     ← Dependencies
```

## 🔧 Files Explained

- **`main.py`** - Main script to run agents
- **`.env`** - AWS credentials (already configured)
- **`config/bedrock_config.py`** - Loads credentials and calls AWS Bedrock
- **`agents/`** - Individual agent files (system prompts, tools, categories)

## 💡 How It Works

```
User runs command
    ↓
main.py loads agent configuration
    ↓
bedrock_config.py loads .env credentials
    ↓
Calls AWS Bedrock API
    ↓
Returns response to user
```

## 🚀 Quick Examples

```bash
# HR Assistant
python3 main.py --agent hr --message "How do I request PTO?"

# Customer Support
python3 main.py --agent customer_support --message "Track my order #12345"

# Travel Planning
python3 main.py --agent travel --message "Plan a 3-day trip to Paris"

# Technical Support
python3 main.py --agent tech_support --message "My laptop won't connect to WiFi"

# Generic Chat
python3 main.py --agent chatbot --message "Tell me a joke"
```

## ⚠️ Important Notes

- `.env` file contains your AWS credentials
- Session tokens expire (usually 1-12 hours)
- Make sure you're in the correct region (`us-west-2` by default)
- First install: `pip install -r requirements.txt`

## 🆘 Troubleshooting

**"ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install -r requirements.txt
```

**"AWS credentials not found"**
```bash
# Check .env file exists
cat .env | grep AWS_ACCESS_KEY_ID
```

**Session expired**
- Get new AWS credentials
- Update `.env` file
- Try again

That's it! Simple and straightforward. 🎉
