---
name: devops
description: "DevOps skill set: GitHub CI/CD pipeline health, Vercel production operations, deployment monitoring, environment management. Never touches application code."
---

# DevOps Skill Set

## Scope

**In scope:**
- GitHub CI/CD: Actions workflows, branch protection, PR checks
- Vercel: deployment status, build logs, runtime logs, environment variables
- Production health monitoring via Vercel CLI

**Out of scope:**
- Writing or reviewing application code (Developer owns this)
- Content pipeline (Writer/Designer/Web Publisher own this)
- Database schema changes (escalate to human engineer)

## Vercel Operations

### Read-only monitoring (safe to run anytime)
```bash
vercel ls                                    # list recent deployments + status
vercel inspect <deployment-url>              # deployment details + build info
vercel logs <deployment-url>                 # runtime logs
vercel env ls production                     # confirm all env vars present
```

### Management operations (require user confirmation)
```bash
vercel env add KEY production                # add environment variable
vercel link --project {slug}                 # link local dir to Vercel project
```

Never run `vercel deploy` or `vercel --prod`. All deployments through `git push` → CI/CD.

## GitHub CI/CD

- Monitor Actions workflows for failures
- Check branch protection rules are in place
- Verify PR checks pass before merge
- Never bypass failing checks

## Escalation Triggers (call a human engineer)
- CI/CD pipeline broken and not resolvable in 2 attempts
- Database schema changes affecting production data
- Security vulnerability in a dependency
- Supabase edge function deployment failures
- Any secret rotation or credential change

## Deployment Model
- All deployments flow through GitHub → Vercel CI/CD only
- Never push to `main` — all changes through PRs
- Never manually promote deployments
- Vercel CLI for read-only operations only; writes through CI/CD
