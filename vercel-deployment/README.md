# Vercel Deployment

A generic skill for safely setting up, deploying, and debugging Vercel projects.

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

The agent should inspect the current repository and ask clarifying questions when multiple valid deployment targets exist. If the repository is not already linked to/deployed on Vercel, the agent should not create, link, connect Git, or deploy until the user confirms that a new setup is desired and clarifies the target account/team/org, project name, app/root directory, and deployment intent.

## Typical workflow

1. Discover repo layout, framework, app root, branch, Vercel scope, env files, and domains.
2. Verify Vercel CLI authentication and check whether the repo is already linked/deployed.
3. If not already linked/deployed, ask for confirmation before creating, linking, connecting Git, or deploying.
4. Create or link the Vercel project only after confirmation.
5. Connect the Git repository only after confirmation.
6. Inspect Vercel's detected settings.
7. Patch incorrect settings explicitly via the Vercel API when needed.
8. Sync environment variables to the correct targets.
9. Add domains if requested.
10. Deploy and monitor logs/status only when deployment is confirmed.

See [SKILL.md](./SKILL.md) for detailed commands and guardrails.
