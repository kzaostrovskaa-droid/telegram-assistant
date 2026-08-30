import openai
from config import OPENAI_API_KEY

client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def summarize_text(text: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Сделай краткую выжимку текста на русском языке. Выдели ключевые моменты и действия."},
            {"role": "user", "content": text[:4000]}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

async def extract_tasks(text: str) -> list:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Из текста извлеки список задач. Верни только список, каждая задача с новой строки, начиная с '- '."},
            {"role": "user", "content": text[:4000]}
        ],
        max_tokens=1000
    )
    content = response.choices[0].message.content
    tasks = [line.strip('- ').strip() for line in content.split('\n') if line.strip().startswith('-')]
    return tasks