# Trustmebro web app

This directory contains the Next.js chat interface and server-side OpenRouter completion endpoint. The Python research agent at the repository root can also use the deployed endpoint through `DEPLOY_API_URL`.

## Run locally

```bash
npm install
npm run dev
```

Set `OPENROUTER_API_KEY` in a local `.env.local` file in this directory before sending a message. `.env.example` lists the supported variables.

## Deploy on Vercel

This repository also contains Python code at its root, so configure Vercel's **Root Directory** as `deploy/trustmebro-prompt-by-tool`.

1. Push this repository to GitHub, GitLab, or Bitbucket and import it in Vercel.
2. Set **Root Directory** to `deploy/trustmebro-prompt-by-tool`.
3. Keep the detected Next.js framework and default build settings.
4. In **Project Settings → Environment Variables**, add `OPENROUTER_API_KEY` with your OpenRouter key for Production. Add it to Preview and Development too if you want those deployments to call the model. Optionally set `OPENROUTER_MODEL` or `OPENROUTER_BASE_URL`.
5. Deploy, then send a message in the deployed app to confirm it can reach OpenRouter.

Keep the key in Vercel's environment settings or in a local `.env.local`; never commit either secret-bearing file. Redeploy after changing Vercel environment variables.

You can also use the Vercel CLI from this directory after linking the project:

```bash
npm install
vercel
vercel --prod
```

To use the deployed completion API from the Python CLI, set `DEPLOY_API_URL` to `https://<your-deployment-domain>/api/complete`, then run `python chat.py --provider openrouter --version v3` from the repository root. The API accepts requests without an `Origin` header (as the Python CLI sends); browser calls from other domains are restricted by the API's CORS allowlist.
