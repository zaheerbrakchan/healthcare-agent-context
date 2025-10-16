import os
from openai import OpenAI


MODEL_TOKEN_LIMITS = {
    "gpt-4": 8192,         # GPT-4 standard
    "gpt-4-32k": 32768,    # GPT-4 extended
    "gpt-3.5-turbo": 4096
}

client = OpenAI(api_key=os.getenv("MYOPENAI_API_KEY"))

def query_llm(system_prompt, user_query):
    print("api_key : ", os.getenv("MYOPENAI_API_KEY"))
    print("client : ",client)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content


def get_model_token_limit(model_name: str = "gpt-4"):
    # Option 1: use predefined map
    if model_name in MODEL_TOKEN_LIMITS:
        return MODEL_TOKEN_LIMITS[model_name]

    # Option 2: dynamically fetch from OpenAI models endpoint
    try:
        info = client.models.retrieve(model_name)
        if hasattr(info, "context_length"):
            return info.context_length
    except Exception as e:
        print("Could not fetch model info:", e)

    # fallback
    return 4096