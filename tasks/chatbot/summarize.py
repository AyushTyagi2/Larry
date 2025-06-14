from transformers import pipeline

# Initialize the summarizer pipeline with a lightweight model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text, max_len=150, min_len=50):
    """
    Summarizes the input text using a pre-trained transformer model.
    
    Args:
        text (str): The text to summarize.
        max_len (int): Maximum length of the summary.
        min_len (int): Minimum length of the summary.
        
    Returns:
        str: The summarized text.
    """
    if len(text.strip()) == 0:
        return "Input text is empty."

    summary = summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)
    return summary[0]['summary_text']


# Test case
if __name__ == "__main__":
    test_text = """
    OpenAI has developed a new version of its GPT model that demonstrates significant improvements 
    in reasoning, problem-solving, and understanding nuanced prompts. This model has been benchmarked 
    against a wide range of tasks and has consistently outperformed previous versions, setting new 
    records in many natural language understanding tasks. The AI research community is excited about 
    the implications this has for the future of human-AI collaboration.
    """

    result = summarize_text(test_text)
    print("Summary:\n", result)
