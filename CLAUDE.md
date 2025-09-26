# Claude Code Instructions for Creative Brief Generator

## Important: Checking Render Logs

**ALWAYS use the Render MCP to check logs** - The Render MCP tools are available and should be used to:
- Check deployment logs
- Monitor application logs for errors
- View build status

To check Render logs:
1. List available MCP resources/tools
2. Look for Render-specific resources
3. Use the appropriate Render MCP tool to fetch logs

## Testing the System

When testing the creative brief generator:
1. **First** - Check Render logs via MCP for any errors
2. **Second** - Check the Coda table for generated data
3. **Third** - Use Puppeteer to submit test URLs through the web interface

## Key Configuration

- **Coda Doc ID**: TeddWcsh5U
- **Coda Table ID**: grid-XSXEqW-PnP
- **GPT Model**: gpt-5-mini (uses reasoning_effort and verbosity parameters, NOT max_tokens)

## Common Commands

- **Run tests**: `npm test` (if available) or `python -m pytest`
- **Check linting**: `npm run lint` or check package.json for lint commands
- **Type checking**: `npm run typecheck` if available

## Environment Notes

- The OpenAI API keys are properly configured in Render's environment
- The custom openai_helper.py bypasses proxy issues in Render
- GPT-5 models require different parameters than GPT-4/3.5