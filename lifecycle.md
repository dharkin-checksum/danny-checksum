# Checksum Lifecycle

## 1. Onboarding Interview

1.1 Pick a repo for us to watch

1.2 Edit the default `checksum.yml` to point to endpoints, and define test output folder and format

## 2. Review Endpoints

Taking in additional knowledge from the customer's codebase and documentation.

## 3. Configure + Validate Auth

## 4. Generate Test Plans

With an associated cost estimate.

## 5. Generate + Review Tests

## 6. Setup Deployment Tracking

## 7. Tests Start Running

## 8. Tests Start Failing

## 9. Test Guru Agent

Uses all provided context from the customer and the history of the test to determine the next step:

- Heal
- Skip
- Slack customer engineers
- Slack customer
- Page customer

## 10. Human-in-the-Loop Memory

If humans are needed, store memory of what action they took. The Test Guru Agent needs to be split into classical and LLM paths, with LLM deferred for model training the "Guru Agent."

## 11. Deployment-Triggered Test Maintenance

When a deployment happens:

- Delete irrelevant tests before they are run (or lazy-evaluate them)
- If endpoints are added, regenerate tests
