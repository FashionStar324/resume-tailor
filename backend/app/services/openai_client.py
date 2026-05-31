from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def get_embedding(text: str) -> list[float]:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000],  # stay within token limit
    )
    return response.data[0].embedding


async def chat_json(system: str, user: str, temperature: float = 0.2) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    import json
    return json.loads(response.choices[0].message.content)


async def chat_stream(system: str, user: str, temperature: float = 0.3):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        stream=True,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
