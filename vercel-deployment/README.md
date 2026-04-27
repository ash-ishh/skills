# Vercel Deployment

A generic skill for setting up, deploying, and debugging Vercel projects.

## When to use

Use this skill when you need to:

- create or link a Vercel project
- connect a Git repository to Vercel
- configure root directory, framework, build command, or output directory
- sync environment variables
- add or inspect domains
- trigger and monitor deployments
- debug Vercel build or runtime failures

## Design goals

This skill is intentionally repository-agnostic. It does not assume:

- a framework such as Next.js
- a monorepo path such as `apps/web`
- GitHub as the Git provider
- `main` as the production branch
- a particular team scope or domain
- a specific `.env` file location

The agent should inspect the current repository and ask clarifying questions when multiple valid deployment targets exist.

## Typical workflow

1. Discover repo layout, framework, app root, branch, Vercel scope, env files, and domains.
2. Verify Vercel CLI authentication.
3. Create or link the Vercel project.
4. Connect the Git repository.
5. Inspect Vercel's detected settings.
6. Patch incorrect settings explicitly via the Vercel API when needed.
7. Sync environment variables to the correct targets.
8. Add domains if requested.
9. Deploy and monitor logs/status.

See [SKILL.md](./SKILL.md) for detailed commands and guardrails.
