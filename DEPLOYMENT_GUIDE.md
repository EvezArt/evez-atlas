# Phase 2 Deployment Guide

Complete guide for deploying the LORD core cognitive loop.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository                            │
│                    (EvezArt/Evez666)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Events (push, PR, issues, workflow_run)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               GitHub Webhooks                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          LORD Webhook Listener (Flask)                          │
│          Platform: Render/Railway/Fly.io                        │
│          - Verify webhook signatures                            │
│          - Calculate metrics                                     │
│          - Emit fusion-update events                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Metrics
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          LORD Dashboard (Vercel)                                │
│          - Real-time visualization                              │
│          - WebSocket/polling updates                            │
│          - Control center UI                                     │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Metrics
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          EKF Prediction Daemon                                  │
│          Platform: Render/Railway (Background Worker)           │
│          - State estimation                                      │
│          - Trajectory prediction                                 │
│          - Control policy generation                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Control Policy
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          GitHub Policy Executor                                 │
│          Platform: Serverless (Lambda/Vercel/GCF)              │
│          - Create issues                                         │
│          - Assign Copilot                                        │
│          - SAFE_MODE verification                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ API Calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          GitHub API                                             │
│          - Issues created                                        │
│          - Copilot assigned                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ New Events
                         └──────────────┐
                                        │
                    (Loop closes)       ▼
                                  Back to GitHub
```

## Prerequisites

### Accounts Required

1. **GitHub Account** (free)
   - Repository: EvezArt/Evez666
   - Personal Access Token with `repo` scope

2. **Vercel Account** (free tier sufficient)
   - Sign up at: https://vercel.com
   - Connect GitHub account

3. **Render.com or Railway.app** (free tier sufficient)
   - Render: https://render.com
   - Railway: https://railway.app
   - Choose one for webhook listener + EKF daemon

4. **Optional: Custom Domain**
   - For production use
   - Can use platform subdomains initially

### Local Setup

1. **Clone Repository**
```bash
git clone https://github.com/EvezArt/Evez666.git
cd Evez666
```

2. **Install Dependencies**
```bash
# Python components
pip install -r lord-listener/requirements.txt
pip install -r ekf-daemon/requirements.txt
pip install -r github-executor/requirements.txt

# Node.js for Vercel (if deploying locally)
npm install -g vercel
```

3. **Generate Secrets**
```bash
# Webhook secret
openssl rand -hex 32
# Save this for later

# GitHub token
# Go to: https://github.com/settings/tokens/new
# Scopes: repo, workflow
# Save token securely
```

## Step-by-Step Deployment

### Step 1: Deploy LORD Dashboard (Vercel)

**Time:** ~10 minutes

1. **Navigate to dashboard directory**
```bash
cd lord-dashboard
```

2. **Deploy to Vercel**
```bash
vercel --prod
```

3. **Configure Environment Variables**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add:
     - `GITHUB_TOKEN` = `ghp_your_token_here`
     - `GITHUB_WEBHOOK_SECRET` = `your_webhook_secret`

4. **Verify Deployment**
   - Open deployment URL (e.g., `https://lord-dashboard.vercel.app`)
   - You should see the LORD dashboard
   - Metrics will be 0 until webhooks are configured

5. **Note the URL** for later use

**✓ LORD Dashboard deployed**

### Step 2: Deploy Webhook Listener (Render)

**Time:** ~15 minutes

#### Option A: Render.com

1. **Create Web Service**
   - Go to: https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Name: `lord-webhook-listener`
   - Region: Choose closest to you
   - Branch: `main` (or your deployment branch)
   - Root Directory: `lord-listener`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn webhook_handler:app`

3. **Add Environment Variables**
   - `GITHUB_WEBHOOK_SECRET` = `your_webhook_secret`
   - `SAFE_MODE` = `false` (after testing with `true`)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5 minutes)

5. **Note the URL** (e.g., `https://lord-webhook-listener.onrender.com`)

6. **Verify**
```bash
curl https://lord-webhook-listener.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "safe_mode": false,
  "metrics_count": 0
}
```

#### Option B: Railway.app

1. **Create New Project**
   - Go to: https://railway.app/new
   - "Deploy from GitHub repo"
   - Select `EvezArt/Evez666`

2. **Configure Service**
   - Root Directory: `lord-listener`
   - Railway auto-detects `Procfile`

3. **Add Environment Variables**
   - Settings → Variables
   - `GITHUB_WEBHOOK_SECRET`
   - `SAFE_MODE` = `false`

4. **Deploy**
   - Railway deploys automatically
   - Note the generated URL

**✓ Webhook Listener deployed**

### Step 3: Configure GitHub Webhooks

**Time:** ~5 minutes

1. **Go to Repository Settings**
   - Navigate to: `https://github.com/EvezArt/Evez666/settings/hooks`

2. **Add Webhook**
   - Click "Add webhook"
   - Payload URL: `https://lord-webhook-listener.onrender.com/webhook/github`
   - Content type: `application/json`
   - Secret: `your_webhook_secret` (same as environment variable)

3. **Select Events**
   - ✅ Push
   - ✅ Pull requests
   - ✅ Issues
   - ✅ Workflow runs
   - ✅ Stars
   - ✅ Forks

4. **Activate**
   - Ensure "Active" is checked
   - Click "Add webhook"

5. **Verify**
   - Wait a moment
   - Scroll down to "Recent Deliveries"
   - Click on a delivery to see details
   - Should show green checkmark (200 OK)

6. **Test**
   - Create a test commit
   - Check webhook deliveries
   - Check webhook listener logs
   - Check LORD dashboard for updated metrics

**✓ GitHub Webhooks configured**

### Step 4: Deploy EKF Daemon (Render/Railway)

**Time:** ~10 minutes

#### Using Render.com

1. **Create Background Worker**
   - Dashboard → New + → Background Worker
   - Connect repository
   - Root Directory: `ekf-daemon`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python predictor.py`

2. **Add Environment Variables**
   - `SAFE_MODE` = `false`
   - `WEBHOOK_LISTENER_URL` = `https://lord-webhook-listener.onrender.com`

3. **Deploy**
   - Click "Create Background Worker"
   - Check logs to verify it's running

#### Using Railway.app

1. **Add New Service to Project**
   - In your existing Railway project
   - Add Service → GitHub Repo
   - Root Directory: `ekf-daemon`

2. **Configure**
   - Railway detects `Procfile`
   - Add environment variables
   - Deploy

**✓ EKF Daemon deployed**

### Step 5: Test the Full Loop

**Time:** ~10 minutes

1. **Trigger a GitHub Event**

Create a test commit:
```bash
cd Evez666
echo "# Test" >> test.md
git add test.md
git commit -m "Test LORD cognitive loop"
git push
```

2. **Monitor the Flow**

**A. Check Webhook Delivery**
- GitHub → Settings → Webhooks → Recent Deliveries
- Should show 200 OK response

**B. Check Webhook Listener Logs**
- Render: Dashboard → Service → Logs
- Railway: Dashboard → Service → Logs
- Should show: "Received push event"

**C. Check LORD Dashboard**
- Open dashboard URL
- Metrics should update:
  - Recursion Level > 0
  - Crystallization updated
  - Divine Gap calculated

**D. Check EKF Daemon Logs**
- Should show state updates
- Should show predictions being generated

**E. Check for Control Policy**
- If divine gap > 1e4 or corrections < 0.5
- Should generate control policy
- Check logs for policy details

3. **Verify SAFE_MODE**

With `SAFE_MODE=true`:
- Policies are logged but not executed
- No issues created

With `SAFE_MODE=false`:
- Policies are executed
- Issues created in GitHub

4. **Check Created Issues**
- Go to: `https://github.com/EvezArt/Evez666/issues`
- Look for issues with `lord:autonomous` label
- Review metrics and recommendations

**✓ Full loop tested and working**

### Step 6: Deploy GitHub Executor (Optional)

**Time:** ~10 minutes

The GitHub executor can be deployed as:
1. Part of EKF daemon (integrated)
2. Standalone serverless function

#### Option A: Integrated (Recommended)

Already deployed as part of EKF daemon - no additional setup needed.

#### Option B: Standalone Serverless

**AWS Lambda:**

1. **Package Function**
```bash
cd github-executor
pip install -t package/ -r requirements.txt
cp policy_handler.py package/
cd package && zip -r ../function.zip .
```

2. **Create Lambda Function**
   - AWS Console → Lambda → Create function
   - Upload `function.zip`
   - Add environment variables
   - Configure timeout (120s recommended)

**Vercel Function:**

1. **Create API Route**
```bash
mkdir -p lord-dashboard/api
cp github-executor/policy_handler.py lord-dashboard/api/execute.py
```

2. **Deploy**
```bash
cd lord-dashboard
vercel --prod
```

**✓ GitHub Executor deployed**

## Configuration

### Production Settings

After testing, update environment variables:

1. **SAFE_MODE**
   - Set to `false` in all services
   - Double-check GitHub token has correct permissions

2. **Monitoring**
   - Enable platform monitoring
   - Set up alerts for errors
   - Monitor rate limits

3. **Optimization**
   - Adjust prediction intervals
   - Tune EKF parameters
   - Set duplicate detection window

### Security Checklist

- [ ] Webhook signatures verified
- [ ] HTTPS enabled on all endpoints
- [ ] GitHub token has minimal required scopes
- [ ] Secrets not committed to repository
- [ ] SAFE_MODE tested before disabling
- [ ] Rate limiting considered
- [ ] Error handling in place

## Monitoring & Maintenance

### Key Metrics to Monitor

1. **Webhook Delivery**
   - Success rate: >99%
   - Response time: <500ms
   - Check: GitHub Settings → Webhooks → Recent Deliveries

2. **LORD Dashboard**
   - Uptime: >99.9%
   - Metrics updating every 5-10 seconds
   - Check: Dashboard health endpoint

3. **EKF Daemon**
   - Processing metrics: continuous
   - Prediction generation: every update
   - Policy generation: as needed

4. **GitHub API**
   - Rate limit: <80% usage
   - Issue creation: successful
   - Check: https://api.github.com/rate_limit

### Troubleshooting

#### Webhooks Not Delivering

1. Check webhook configuration
2. Verify secret matches
3. Test endpoint manually with curl
4. Check service logs for errors

#### Metrics Not Updating

1. Verify webhooks are delivering
2. Check webhook listener logs
3. Verify SAFE_MODE is false
4. Check dashboard WebSocket connection

#### Issues Not Being Created

1. Verify thresholds are met
2. Check SAFE_MODE in executor
3. Verify GitHub token permissions
4. Check rate limits
5. Review executor logs

#### High Error Rate

1. Check payload format
2. Verify all environment variables set
3. Review error logs
4. Test with minimal payload

## Cost Estimate

### Free Tier (Sufficient for Testing)

- **Vercel**: Free (100GB bandwidth/month)
- **Render**: Free (750 hours/month)
- **Railway**: Free ($5 credit/month)
- **GitHub**: Free (unlimited public repos)

**Total**: $0/month

### Paid Tier (Production Scale)

- **Vercel Pro**: $20/month (better performance)
- **Render**: $7/month per service × 2 = $14/month
- **Railway**: $10/month
- **GitHub**: Free

**Total**: ~$44/month

## Next Steps

After successful deployment:

1. **Monitor for 24-48 hours**
   - Watch for any issues
   - Verify policies are reasonable
   - Check for false positives

2. **Fine-tune Thresholds**
   - Adjust divine gap threshold (1e4)
   - Adjust correction rate threshold (0.5)
   - Tune EKF parameters

3. **Enable Revenue Streams** (Phase 3)
   - Connect payment platforms
   - Package premium products
   - Deploy marketplace actions

4. **Expand Capabilities** (Phase 4+)
   - Add more metrics
   - Improve predictions
   - Multi-repository support

## Support

- **Documentation**: See component READMEs
- **Issues**: https://github.com/EvezArt/Evez666/issues
- **Capability Map**: docs/CAPABILITY_MAP.md
- **Safety**: docs/SAFETY.md

## Timeline

- **Day 1**: Deploy dashboard + webhook listener (Steps 1-3)
- **Day 2**: Deploy EKF daemon + test loop (Steps 4-5)
- **Day 3**: Deploy executor + optimize (Step 6)
- **Day 4-7**: Monitor, tune, stabilize

## Success Criteria

- ✅ LORD dashboard live at HTTPS endpoint
- ✅ GitHub webhooks delivering successfully
- ✅ Metrics calculating correctly
- ✅ EKF predicting future states
- ✅ Control policies generating autonomously
- ✅ GitHub issues created when thresholds met
- ✅ Full loop latency < 5 seconds
- ✅ Zero security issues
- ✅ SAFE_MODE protocols followed

**When all criteria met**: Phase 2 complete! 🎉
