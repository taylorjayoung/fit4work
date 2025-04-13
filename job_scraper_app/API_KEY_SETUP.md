# Secure API Key Management

This document explains how to securely manage your Anthropic API key and other sensitive credentials in the Fit4Work application without exposing them in your GitHub repository.

## Why This Matters

API keys and other credentials should never be committed to public (or even private) repositories because:

1. **Security Risk**: Exposed API keys can be found by malicious actors who scan GitHub repositories
2. **Credential Leakage**: Once a key is committed to Git history, it's difficult to completely remove
3. **Compliance Issues**: Exposing API keys may violate terms of service for the API provider
4. **Potential Costs**: Compromised API keys can lead to unauthorized usage and unexpected charges

## How to Set Up Your API Keys

You have several options for securely providing your Anthropic API key:

### Option 1: Use a .env File (Recommended)

1. Create a copy of the template file:

   ```bash
   cp job_scraper_app/.env.example job_scraper_app/.env
   ```

2. Edit `job_scraper_app/.env` and replace the placeholder with your real API key:

   ```
   FIT4WORK_ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

3. This file is listed in `.gitignore` and will not be committed to the repository.

### Option 2: Use Environment Variables

1. Set the `FIT4WORK_ANTHROPIC_API_KEY` environment variable in your shell:

   ```bash
   # For Linux/macOS (add to your .bashrc, .zshrc, etc.)
   export FIT4WORK_ANTHROPIC_API_KEY="your-actual-api-key"
   
   # For Windows (Command Prompt)
   set FIT4WORK_ANTHROPIC_API_KEY=your-actual-api-key
   
   # For Windows (PowerShell)
   $env:FIT4WORK_ANTHROPIC_API_KEY="your-actual-api-key"
   ```

2. The application will automatically detect and use this environment variable.

### Option 2: Use a Local Config File

1. Create a copy of the template file:

   ```bash
   cp job_scraper_app/config.local.json.template job_scraper_app/config.local.json
   ```

2. Edit `job_scraper_app/config.local.json` and replace `YOUR_ACTUAL_ANTHROPIC_API_KEY` with your real API key:

   ```json
   {
     "ai_services": {
       "anthropic": {
         "api_key": "your-actual-api-key"
       }
     }
   }
   ```

3. This file is listed in `.gitignore` and will not be committed to the repository.

### Option 3: Modify config.json Directly (Not Recommended for Shared Repositories)

If you're working on a private repository that will never be shared:

1. Edit `job_scraper_app/config.json` and replace `YOUR_ANTHROPIC_API_KEY` with your real API key.
2. Be careful not to commit this file to GitHub.

## How It Works

The application uses a configuration loading system that checks multiple sources in the following order of priority:

1. Environment variables (highest priority)
2. `config.local.json` (if it exists)
3. `config.json` (lowest priority)

This means that if you set your API key in an environment variable, it will override any values in the config files.

## For Development Teams

If you're working in a team:

1. Use `config.example.json` as a template showing the required structure
2. Each developer should create their own `config.local.json` or use environment variables
3. Never commit real API keys to the repository
4. Consider using a secure credential management system for production deployments

## Verifying Your Setup

To verify that your API key is being loaded correctly, you can run the application and check the logs. If the API key is loaded successfully, you should see API requests working without authentication errors.
