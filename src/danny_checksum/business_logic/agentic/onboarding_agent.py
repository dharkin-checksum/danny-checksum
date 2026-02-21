import json

from pydantic_ai import Agent

from danny_checksum.connectors.database import onboarding_dao

_SALES_INSTRUCTIONS = """\
You are an onboarding assistant for Checksum, chatting with a sales \
colleague. Your job is to collect as much information as possible about a new \
customer before the customer interview begins.

Ask about each of these topics in a natural, conversational way:
- customer_name — the customer's company or project name
- repository — the GitHub repository (owner/repo format)
- api_endpoints — the API endpoints to be tested (collect as a list)
- auth_method — how the API authenticates (e.g. API key, OAuth, JWT)
- auth_details — specifics like where to put the key, scopes needed, etc.
- test_output_folder — where generated test files should be saved
- test_output_format — preferred test framework/format (e.g. pytest, jest)
- test_descriptions — high-level descriptions of what to test (collect as a list)
- additional_context — anything else useful (conventions, quirks, priorities)

It's completely fine if the sales colleague doesn't know some answers — just \
acknowledge that gracefully and move on. Use the save_answer tool to persist \
each piece of information as you receive it. Use get_current_state and \
list_unanswered_questions to track progress.

only ask about test_output_folder if they specify repository 

Keep the tone collegial and friendly. When all questions have been addressed \
(answered or skipped), summarise what was collected and let the colleague know \
the customer interview can now begin.\
"""

_CUSTOMER_INSTRUCTIONS = """\
You are an onboarding assistant for Checksum, interviewing a customer to \
set up their automated test generation. A sales colleague has already provided \
some initial information.

Start by using get_current_state to see what's already been collected, then \
use list_unanswered_questions to identify gaps.

Your goals:
1. Confirm the information already provided is correct.
2. Fill in any missing fields by asking the customer directly.
3. Gather any additional context that would help generate better tests.

The fields you're collecting:
- customer_name — the customer's company or project name
- repository — the GitHub repository (owner/repo format)
- api_endpoints — the API endpoints to be tested (collect as a list)
- auth_method — how the API authenticates (e.g. API key, OAuth, JWT)
- auth_details — specifics like where to put the key, scopes needed, etc.
- test_output_folder — where generated test files should be saved
- test_output_format — preferred test framework/format (e.g. pytest, jest)
- test_descriptions — high-level descriptions of what to test (collect as a list)
- additional_context — anything else useful (conventions, quirks, priorities)

Keep the tone professional and respectful. Use the save_answer tool to persist \
each piece of information. When all fields are filled, summarise the complete \
onboarding profile and confirm with the customer.\
"""


def create_agent(role: str, session_id: int) -> Agent:
    """Create an onboarding agent.

    Args:
        role: "sales" for the sales-colleague interview,
              "customer" for the customer interview.
        session_id: ID of the OnboardingSession to read/write.
    """
    if role == "sales":
        instructions = _SALES_INSTRUCTIONS
    elif role == "customer":
        instructions = _CUSTOMER_INSTRUCTIONS
    else:
        raise ValueError(f"Unknown role: {role!r}. Must be 'sales' or 'customer'.")

    agent = Agent("anthropic:claude-sonnet-4-6", instructions=instructions)

    @agent.tool_plain
    def save_answer(field_name: str, value: str) -> str:
        """Save an answer for a specific onboarding field.

        Args:
            field_name: One of the onboarding fields (e.g. 'customer_name').
            value: The value to store. For list fields (api_endpoints,
                   test_descriptions), pass a JSON array string.
        """
        try:
            # Try to parse JSON for list fields
            if field_name in ("api_endpoints", "test_descriptions"):
                try:
                    parsed = json.loads(value)
                    onboarding_dao.update_field(session_id, field_name, parsed)
                except json.JSONDecodeError:
                    onboarding_dao.update_field(session_id, field_name, value)
            else:
                onboarding_dao.update_field(session_id, field_name, value)
            return f"Saved {field_name} successfully."
        except ValueError as e:
            return str(e)

    @agent.tool_plain
    def get_current_state() -> str:
        """Return the current state of all collected onboarding information as JSON."""
        data = onboarding_dao.get_onboarding_session(session_id)
        if data is None:
            return "Session not found."
        return json.dumps(data, indent=2)

    @agent.tool_plain
    def list_unanswered_questions() -> str:
        """Return a JSON list of field names that still need answers."""
        try:
            fields = onboarding_dao.get_unanswered_fields(session_id)
            return json.dumps(fields)
        except ValueError as e:
            return str(e)

    return agent
