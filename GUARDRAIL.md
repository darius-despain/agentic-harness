# Soft Guardrail Config — ~/workspace only

WORKSPACE_ROOT=/home/ddespain/workspace
CONFIRMATION_POLICY=AlwaysConfirm (or ConfirmRisky + LLMSecurityAnalyzer)

Rules:
- Only create/edit files under ~/workspace or its subdirectories.
- Before any destructive action (delete, modify outside workspace, install globally), confirm with user.
- Don't read/write outside /home/ddespain/workspace unless explicitly asked.
