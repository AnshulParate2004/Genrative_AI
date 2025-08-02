from ollama import Client

client = Client(host="http://localhost:11434")

print("Pulling model gemma3:1b...")
client.pull('gemma3:1b')
print("Model pulled!")

response = client.chat(
    model="gemma3:1b",
    messages=[{"role": "user", "content": "Hey there!"}],
)

print("Model response:", response['message']['content'])
