def preprocess_input(title, text, subject, date):
    return {
        "title": title.strip(),
        "text": text.strip(),
        "subject": subject.strip(),
        "date": str(date)
    }
