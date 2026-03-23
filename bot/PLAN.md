# LMS Telegram Bot Development Plan

## Overview
This bot provides LMS analytics and student support via Telegram, integrating with the LMS backend API and Qwen Code LLM for intelligent responses.

## Architecture
- **Testable Handlers**: Command logic separated from Telegram transport layer
- **--test Mode**: CLI mode for debugging without Telegram
- **Services Layer**: API client for LMS backend, LLM client for Qwen Code
- **Config**: Environment-based configuration with .env.bot.secret

## Tasks Breakdown

### Task 1: Scaffold (Current)
- Create bot directory structure
- Implement handlers with placeholder responses
- Add --test mode for offline verification
- Setup pyproject.toml with dependencies

### Task 2: Backend Integration
- Implement real LMS API calls for /scores, /stats
- Add proper error handling
- Integrate with Telegram via python-telegram-bot

### Task 3: Intent Routing with LLM
- Use Qwen Code API to interpret natural language queries
- Route to appropriate commands or generate responses
- Fallback to help when unclear

## Testing Strategy
1. Local test mode: `uv run bot.py --test "/command"`
2. Integration with actual backend (VM)
3. Full Telegram deployment

## Deployment
- Bot runs as background process on VM: `nohup uv run bot.py > bot.log 2>&1 &`
- Config stored in .env.bot.secret (not committed)
- Auto-restart via systemd or supervisor (optional)

This scaffold ensures maintainable, testable code that can be extended for all lab requirements.
