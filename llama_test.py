from youtube_transcript_api import YouTubeTranscriptApi
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments

# Function to test the model with test sentences
def test_model(model, tokenizer, test_sentences):
    print("Testing model...")
    model.to('cpu')  # Move the model to CPU
    for sentence in test_sentences:
        input_ids = tokenizer.encode(sentence, return_tensors="pt").to('cpu')  # Ensure input_ids are on CPU
        attention_mask = torch.ones_like(input_ids).to('cpu')  # Ensure attention_mask is on CPU
        output = model.generate(input_ids, attention_mask=attention_mask, max_length=50, num_return_sequences=1)
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        print(f"Input: {sentence}\nOutput: {generated_text}\n")


# print("Fetching YouTube transcripts...")
# List of YouTube video URLs
urls = [
    "https://www.youtube.com/watch?v=2pMc8NOd2Xw",
    "https://www.youtube.com/watch?v=Z_zl6TAl6Uw",
    "https://www.youtube.com/watch?v=vaMRtwz8tP8",
    "https://www.youtube.com/watch?v=ZdFGeHak7cI",
    "https://www.youtube.com/watch?v=klfMy_eNOvw",
    "https://www.youtube.com/watch?v=PmlX79bG6Zo",
    "https://www.youtube.com/watch?v=Z1hnCxUAH7I",
    "https://www.youtube.com/watch?v=SvK9nJ2G478",
    "https://www.youtube.com/watch?v=2frAVVPrMLQ",
    "https://www.youtube.com/watch?v=tc8neBBzG58",
    "https://www.youtube.com/watch?v=sIodt4i5RfU",
    "https://www.youtube.com/watch?v=KSVFVjg-M-A",
    "https://www.youtube.com/watch?v=6Kf3mh8zNMU",
    "https://www.youtube.com/watch?v=cCZ1jalRkzI",
    "https://www.youtube.com/watch?v=RKM7dkLehAg",
    "https://www.youtube.com/watch?v=z6X7demVALo",
    "https://www.youtube.com/watch?v=ZI2YHkBe8bk",
    "https://www.youtube.com/watch?v=7JyZSwLWLaI"
]

# Extract video IDs from URLs
video_ids = [url.split("v=")[-1] for url in urls]

# # Fetch transcripts and save to a file
max_length = 1024  # Set the maximum length
with open("youtube_transcripts.txt", "w") as file:
    for video_id in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = ' '.join([t['text'].strip() for t in transcript])
            # Split or truncate the text to fit the maximum length
            for i in range(0, len(text), max_length):
                file.write(text[i:i+max_length] + "\n")
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {e}")

print("Loading model and tokenizer...")
os.environ["HF_HOME"] = "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"

# Load tokenizer and model
model_name = "meta-llama/Llama-2-7b"
tokenizer = AutoTokenizer.from_pretrained(model_name, force_download = True)
model = AutoModelForCausalLM.from_pretrained(model_name, force_download = True)

# Define test sentences specific to soccer and Manchester United
test_sentences = [
    "Manchester United's strategy for the next match",
    "Replace blank with something that makes sense: Blank scored an amazin goal!"
    "Analysis of Manchester United's recent performance",
    "Who scored the winning goal in the last Manchester United match?",
    "What was the final score of the Manchester United vs. Liverpool match?",
    "How many saves did David de Gea make in the last match?",
    "Who provided the assist for the first goal in the last match?",
    "Which player was named Man of the Match in the last Manchester United game?"
]

# Test the model before fine-tuning
print("Testing model before fine-tuning:\n")
test_model(model, tokenizer, test_sentences)

# Prepare dataset
print("Preparing dataset...")
dataset = TextDataset(
    tokenizer=tokenizer,
    file_path="youtube_transcripts.txt",
    block_size=64
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, 
    mlm=False
)

# Set up training arguments
print("Setting up training arguments...")
training_args = TrainingArguments(
    output_dir="./output",
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=4,  # Adjust based on your system's memory
    save_steps=10_000,
    save_total_limit=2,
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
)

# Start fine-tuning
print("Starting fine-tuning...")
trainer.train()

model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

# Test the model after fine-tuning
print("Testing model after fine-tuning:\n")
test_model(model, tokenizer, test_sentences)
