from huggingface_hub import InferenceClient

client = InferenceClient(model="Qwen/Qwen2.5-Math-1.5B-Instruct", token="HF_TOKEN")

response = client.text_generation("Find the value of x that satisfies 4x+5=6x+7")
print(response)
