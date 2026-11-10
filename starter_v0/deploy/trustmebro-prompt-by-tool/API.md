# OpenRouter completion API

The Next.js app exposes `POST /api/complete`. It keeps the OpenRouter key on the server and returns normalized text and tool calls for the CLI.

Set `OPENROUTER_API_KEY` in the deployment environment (or in a local `.env.local` file in this directory), then start the app with `npm run dev`.

Example request:

```json
{
  "provider": "openrouter",
  "version": "v3",
  "model": "openai/gpt-4o-mini",
  "messages": [{"role": "user", "content": "Hello"}],
  "tools": [],
  "temperature": 0
}
```

The response shape is `{ "version": "v3", "model": "...", "text": "...", "tool_calls": [{"name": "...", "args": {}}] }`.

From the repository root, point `DEPLOY_API_URL` to the deployed API or its local development server and run:

```powershell
$env:DEPLOY_API_URL = "http://localhost:3000/api/complete"
python chat.py --provider openrouter --version v3
```
