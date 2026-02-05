# Automation Assistant Telemetry Debrief

**Generated:** debrief.py

## Overall Health

- **Status:** 🟢 OK
- **Total Runs:** 2
- **Total Events:** 10
- **Success:** 10
- **Errors:** 0
- **Failure Rate:** 0.00%

## Per-Backend Statistics

### ChatGPT (gpt-3.5-turbo)

- **Total Calls:** 3
- **Success:** 3
- **Errors:** 0
- **Failure Rate:** 0.00%
- **Average Latency:** 334.56 ms
- **P50 Latency:** 501.50 ms
- **P95 Latency:** 502.16 ms

### Comet (comet-v1)

- **Total Calls:** 3
- **Success:** 3
- **Errors:** 0
- **Failure Rate:** 0.00%
- **Average Latency:** 267.77 ms
- **P50 Latency:** 401.24 ms
- **P95 Latency:** 402.07 ms

### Local (local-mock)

- **Total Calls:** 4
- **Success:** 4
- **Errors:** 0
- **Failure Rate:** 0.00%
- **Average Latency:** 50.38 ms
- **P50 Latency:** 50.19 ms
- **P95 Latency:** 101.14 ms

## Metrics Explanation

- **Failure Rate:** Percentage of operations that resulted in errors
- **P50 Latency:** Median response time (50th percentile)
- **P95 Latency:** 95th percentile response time

## Health Verdicts

- 🟢 **OK**: Failure rate < 5%
- 🟡 **Degraded**: Failure rate 5-20%
- 🔴 **Critical**: Failure rate > 20%
