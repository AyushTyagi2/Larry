from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the GPT-2 Small model and tokenizer
model_name = "gpt2"  # GPT-2 Small
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def generate_email(subject: str):
    # Adjust the prompt to make it clearer and more focused
    prompt = f"Write a polite and professional email to {recipient} requesting {subject}. The email should be formal and should only include relevant information about the sick leave request."
    
    # Encode the input prompt
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    # Generate the output using the model
    outputs = model.generate(inputs, max_length=200, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.9, top_k=50)
    
    # Decode the output and return as text
    email_content = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return email_content

# Example usage
subject = "sick leave for two days"
recipient = "2023csb1108@iitrpr.ac.in"
#generated_email = generate_email(subject, recipient)
