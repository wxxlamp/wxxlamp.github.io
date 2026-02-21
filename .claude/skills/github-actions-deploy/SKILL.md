---
name: github-actions-deploy
description: Configure and manage GitHub Actions automated deployment workflows for Hexo blog.
license: Apache-2.0
metadata:
  author: Claude
  version: "1.0"
---

# GitHub Actions Deployment Skill

Configure and manage GitHub Actions automated deployment workflows for Hexo blog.

## Prerequisites

1. **Dependencies**: Git, GitHub repository access
2. **Configuration**: Access to GitHub repository settings and secrets

    **Configuration File**: `config/_deployment_config.json`
    ```json
    {
      "source_branch": "deploy",
      "target_branch": "master",
      "workflow_file": ".github/workflows/deploy.yml",
      "github_token_secret": "GITHUB_TOKEN"
    }
    ```

## Usage

To setup GitHub Actions deployment, create the workflow file manually or follow these steps.

### Setup Steps

1. **Create workflow directory** (if not exists)
   ```bash
   mkdir -p .github/workflows
   ```

2. **Create the workflow file** `.github/workflows/deploy.yml` with the content below

3. **Configure GitHub Secrets** (if needed)
   - Go to repository Settings → Secrets and Variables → Actions
   - Add any required secrets (e.g., `GITHUB_TOKEN`)

4. **Push to trigger deployment**
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Add GitHub Actions deployment workflow"
   git push origin deploy
   ```

## Workflow Configuration

The workflow file should be placed at `.github/workflows/deploy.yml`.

### Configuration Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `source_branch` | Source branch that triggers deployment | `deploy` |
| `target_branch` | Target branch for GitHub Pages | `master` |
| `node_version` | Node.js version for build | `22` |

### Example Workflow File

See [deploy.yml.example](deploy.yml.example) for a complete template.

## Output

**Success:**
```text
✅ GitHub Actions Deployment Setup Successful!
Workflow File: .github/workflows/deploy.yml
Source Branch: deploy
Target Branch: master
Deployment Trigger: On push to source branch
```

**Failure:**
```text
❌ GitHub Actions Deployment Setup Failed
Message: Missing repository access or invalid configuration.
```

## Process Flow

1. Validate repository access and permissions
2. Create GitHub Actions workflow file
3. Configure build and deployment steps for Hexo
4. Set up triggers and environment variables
5. Verify workflow syntax and initial run
6. Return setup results