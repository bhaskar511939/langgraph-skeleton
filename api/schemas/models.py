# Allowed model identifiers.
# Add your provider's model names here.
# Format depends on your OPENAI_BASE_URL provider.
ALLOWED_MODELS: set[str] = {
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "claude-opus-4-8",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
}
