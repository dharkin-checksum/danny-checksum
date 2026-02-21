# Checksum Lifecycle

## 1. Sales Inputs

Sales inputs everything they've learned.

## 2. Onboarding Interview

### 2.1 Pick a repo for us to watch

### 2.2 Edit the default `checksum.yml` to point to endpoints, and define test output folder and format

## 3. Review Endpoints

Taking in additional knowledge from the customer's codebase and documentation.

## 4. Configure + Validate Auth

## 5. Generate Test Plans

With an associated cost estimate.

## 6. Generate + Review Tests

## 7. Setup Deployment Tracking

## 8. Tests Start Running

## 9. Tests Start Failing

## 10. Test Guru Agent

Uses all provided context from the customer and the history of the test to determine the next step:

- Heal
- Skip
- Slack customer engineers
- Slack customer
- Page customer

## 11. Human-in-the-Loop Memory

If humans are needed, store memory of what action they took. The Test Guru Agent needs to be split into classical and LLM paths, with LLM deferred for model training the "Guru Agent."

## 12. Deployment-Triggered Test Maintenance

When a deployment happens:

- Delete irrelevant tests before they are run (or lazy-evaluate them)
- If endpoints are added, regenerate tests
