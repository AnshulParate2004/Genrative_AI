import tiktoken

encoder = tiktoken.encoding_for_model('gpt-4o')

print("Vocab Size",encoder.n_vocab)

text = "the cat sat on the mat"
token = encoder.encode(text) 
print ("Encoded",token)

coded = [3086, 9059, 10139, 402, 290, 2450]
decoded = encoder.decode(coded)
print ("Decoded",decoded)
