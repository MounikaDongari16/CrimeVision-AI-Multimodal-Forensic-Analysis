from utils.groq_utils import get_groq_client, get_config

def translate_transcript(text):
    """
    Translate transcript into Telugu, Hindi, and French using Groq
    """
    client = get_groq_client()
    config = get_config()
    languages = config["languages"]
    
    translations = {"english": text}
    
    for lang in languages:
        prompt = f"Translate the following English crime scene witness statement into {lang}. Return ONLY the translated text.\n\nText: {text}"
        
        try:
            completion = client.chat.completions.create(
                model=config["groq_model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            translations[lang.lower()] = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Translation failed for {lang}: {str(e)}")
            translations[lang.lower()] = f"Error: {str(e)}"
            
    return translations
