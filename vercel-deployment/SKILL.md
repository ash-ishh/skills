---
name: vercel-deployment
description: Deploy and troubleshoot projects on Vercel in a repo-agnostic way. Use when setting up Vercel projects, connecting Git repos, configuring framework/root directory/build settings, syncing environment variables, adding domains, triggering deployments, or debugging Vercel build/runtime failures.
---

# Vercel Deployment

Use this skill to deploy, maintain, or troubleshoot Git-backed projects on Vercel without assuming a specific repository layout, framework, team, domain, or environment file location.

## Core principle

Discovery and confirmation come before creation or deployment. First determine whether the repo is already linked to an existing Vercel project or has prior deployments. If it is not already deployed/linked, do **not** create/link/deploy automatically. Ask the user to confirm that they want a new Vercel setup and clarify any ambiguous choices such as target org/account/team, project name, app/root directory, production branch, environment targets, and domain.

Do not hard-code paths like `apps/web`, frameworks like `nextjs`, branches like `main`, team scopes, domains, or env file names unless the user or repository configuration confirms them.

## 1) Discover the project

From the repository root, inspect the app before deploying:

```bash
pwd
git remote -v
git branch --show-current
find . -maxdepth 3 \( -name package.json -o -name vercel.json -o -name next.config.* -o -name vite.config.* -o -name astro.config.* -o -name svelte.config.* -o -name nuxt.config.* \) -print
```

Identify:

- repository URL and provider
- project name
- intended app/root directory (`.` for single app repos, a subdirectory for monorepos)
- framework preset, if any
- build command, output directory, install command, and development command if the defaults are not enough
- production branch
- target Vercel scope/team
- required environment variables and domains

If multiple apps are present, ask which app should be deployed.

## 2) Verify Vercel auth, scope, and existing project state

```bash
vercel whoami
vercel teams ls
find . -maxdepth 3 -path '*/.vercel/project.json' -print
```

If a `.vercel/project.json` exists, inspect it before acting:

```bash
cat .vercel/project.json
vercel project inspect <project-name-or-id> [--scope <team-slug>]
```

If deploying under a team, pass `--scope <team-slug>` on all relevant commands. If using a personal account, omit `--scope`.

If the project is not already linked or the scope cannot be inferred, stop and ask for confirmation instead of guessing. Useful questions include:

- Should I set this up as a new Vercel project, or only work with an existing one?
- Which Vercel account/team/org should own it?
- What project name should be used?
- Which app/root directory should be linked?
- Which branch should be production?
- Should I trigger a deployment now, or only configure/link the project?

## 3) Create or link the Vercel project only after confirmation

Prefer running commands from the repository root and using `--cwd <root-directory>` only when needed.

Only run these commands when one of the following is true:

- the repository is already linked to the intended Vercel project and scope, or
- the user has explicitly confirmed a new setup and answered the necessary ownership/project/root-directory questions.

```bash
vercel project add <project-name> [--scope <team-slug>]
vercel link [--project <project-name>] [--scope <team-slug>] [--cwd <root-directory>]
```

For Git-backed deployments, connect the repo only if it is not already connected and the user has confirmed the target account/team/project:

```bash
vercel git connect <repo-url> [--scope <team-slug>] [--cwd <root-directory>]
```

## 4) Configure project settings explicitly when defaults are wrong

Vercel auto-detection can be wrong in monorepos or non-standard layouts. Inspect first:

```bash
vercel project inspect <project-name> [--scope <team-slug>]
vercel api /v9/projects/<project-name> [--scope <team-slug>] --raw
```

Patch only the settings that need to be corrected. Example payload:

```bash
cat > /tmp/vercel-project-patch.json <<'JSON'
{
  "framework": "<framework-or-null>",
  "rootDirectory": "<root-directory>",
  "buildCommand": "<build-command-or-null>",
  "outputDirectory": "<output-directory-or-null>",
  "installCommand": "<install-command-or-null>",
  "devCommand": "<dev-command-or-null>"
}
JSON

vercel api /v9/projects/<project-name> \
  [--scope <team-slug>] \
  -X PATCH \
  --input /tmp/vercel-project-patch.json \
  --raw
```

Remove keys that are unknown or should use Vercel defaults. Do not send placeholder values.

Common framework values include `nextjs`, `vite`, `sveltekit`, `astro`, `nuxtjs`, `remix`, and `other`. Confirm the exact value supported by the current Vercel API/CLI before patching.

## 5) Environment variables

Find the repo's env examples and local env files:

```bash
find . -maxdepth 4 \( -name '.env' -o -name '.env.*' -o -name '*env.example' -o -name '*env.sample' \) -print
```

Rules:

- Never print secrets in chat or logs.
- Prefer env example files to determine required keys.
- Use local env files only as secret sources when the user authorizes it.
- Sync each required key to the correct Vercel targets: `production`, `preview`, and/or `development`.
- If a variable already exists, use `vercel env update` rather than duplicating it.

Useful commands:

```bash
vercel env list [production|preview|development] [--scope <team-slug>] [--cwd <root-directory>]
vercel env add <KEY> <target> [--scope <team-slug>] [--cwd <root-directory>]
vercel env update <KEY> <target> [--scope <team-slug>] [--cwd <root-directory>]
vercel api /v10/projects/<project-name>/env?target=<target> [--scope <team-slug>] --raw
```

If project metadata exposes a generated project ID that the app needs, add it only when the app explicitly requires it.

## 6) Domains

Add domains only after confirming the desired hostnames with the user or repo documentation.

```bash
cat > /tmp/vercel-domain.json <<'JSON'
{"name":"<domain>"}
JSON

vercel api /v10/projects/<project-name>/domains \
  [--scope <team-slug>] \
  -X POST \
  --input /tmp/vercel-domain.json \
  --raw

vercel api /v9/projects/<project-name>/domains [--scope <team-slug>] --raw
```

Check DNS verification instructions from Vercel before declaring the domain complete.

## 7) Trigger deployment

Only trigger a deployment when the project is already linked/deployed or the user has explicitly asked to deploy after confirming the Vercel account/team/project/root-directory choices. If no existing Vercel project/deployment is found, ask before deploying.

Use the simplest valid deployment path first:

```bash
vercel deploy [--prod] [--scope <team-slug>] [--cwd <root-directory>]
```

If CLI deployment has path or monorepo linking issues, create a Git-backed deployment via API:

```bash
cat > /tmp/vercel-deployment.json <<'JSON'
{
  "name": "<project-name>",
  "target": "production",
  "gitSource": {
    "type": "github",
    "repo": "<repo-name>",
    "org": "<org-or-user>",
    "ref": "<branch-or-sha>"
  },
  "project": "<project-id>"
}
JSON

vercel api /v13/deployments \
  [--scope <team-slug>] \
  -X POST \
  --input /tmp/vercel-deployment.json \
  --raw
```

Adjust `gitSource.type` and fields for the connected Git provider. Do not assume GitHub.

## 8) Monitor and debug

```bash
vercel inspect <deployment-id-or-url> [--scope <team-slug>]
vercel inspect <deployment-id-or-url> [--scope <team-slug>] --logs
vercel api /v13/deployments/<deployment-id> [--scope <team-slug>] --raw
```

Check:

- build status / ready state
- build logs
- framework/root/build/output settings
- missing or mis-scoped environment variables
- unsupported Node/package manager versions
- domain/DNS verification status

## Common pitfalls

- Creating, linking, or deploying a new Vercel project when the repo was not already deployed and the user has not confirmed the target account/team/project.
- Assuming a monorepo app path instead of discovering it.
- Assuming the framework preset instead of inspecting config files.
- Running `vercel link` from a subdirectory and later deploying from a different directory.
- Forgetting `--scope` for team projects.
- Importing secrets from the wrong env file or target.
- Treating a successful build as proof that runtime env vars are complete.
- Adding domains before DNS ownership/verification is ready.

## Minimal checklist

- Discover repo, app root, framework, branch, scope, env requirements, and domains.
- Verify Vercel login, team scope, and whether the repo is already linked/deployed.
- If not already linked/deployed, ask before creating, linking, connecting Git, or deploying.
- Create/link the project only after confirmation.
- Connect the Git repository only after confirmation.
- Inspect and patch Vercel project settings only where needed.
- Sync required environment variables to the correct targets.
- Add and verify domains if requested.
- Deploy.
- Inspect logs and raw deployment status until ready.
