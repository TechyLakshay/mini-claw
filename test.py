from groq import Groq
print(Groq(api_key="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").chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role":"user","content":"write a code  for printing fabonacci series in python"}]
).choices[0].message.content) 