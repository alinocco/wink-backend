import spacy


class Lemmatizer:
    def __init__(self):
        self.nlp = spacy.load('ru_core_news_md')

    def lemmatize(self, text: str):
        doc = self.nlp(text)
        return ' '.join([token.lemma_ for token in doc])