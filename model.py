from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
from datasets import Dataset
import torch

# Load the pre-trained GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Set a padding token
tokenizer.pad_token = tokenizer.eos_token  # Use the EOS token as the padding token

# Load and prepare your book data (replace 'rumi_life.txt' with your actual file path)
with open('/content/rumi_life.txt', 'r') as file:
    text = file.read()

# Tokenize the text data in chunks
def tokenize_text(text, tokenizer, max_length=512):
    tokenized_texts = []
    tokens = tokenizer.encode(text, truncation=True, max_length=max_length, return_tensors='pt')
    for i in range(0, len(tokens[0]), max_length):
        chunk = tokens[:, i:i + max_length]
        tokenized_texts.append(chunk.squeeze())
    return tokenized_texts

# Tokenize and create dataset
tokenized_texts = tokenize_text(text, tokenizer)
data = {
    'input_ids': [t.tolist() for t in tokenized_texts],
    'attention_mask': [torch.ones_like(t).tolist() for t in tokenized_texts],
    'labels': [t.tolist() for t in tokenized_texts]  # Labels are the same as input_ids
}

# Wrap data in a Hugging Face Dataset object
dataset = Dataset.from_dict(data)

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',          # Directory to save the model
    overwrite_output_dir=True,       # Overwrite previous models in the directory
    num_train_epochs=3,              # Number of training epochs
    per_device_train_batch_size=1,   # Batch size per device
    save_steps=10_000,               # Save every 10,000 steps
    save_total_limit=2,              # Save only the last 2 checkpoints
    logging_dir='./logs',            # Log directory
    logging_steps=200                # Log every 200 steps
)

# Create Trainer object
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)
# Fine-tune the model on your book
trainer.train()

# Save the model and tokenizer
model.save_pretrained('./fine_tuned_model')
tokenizer.save_pretrained('./fine_tuned_model')

# Testing the fine-tuned model with a prompt (interactive prompt response)
prompt = "What does Rumi say about love?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(inputs['input_ids'], max_length=100, num_return_sequences=1)

# Decode the generated text
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
