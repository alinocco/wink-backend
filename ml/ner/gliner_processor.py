from fsspec.registry import default
from gliner import GLiNER
from ner.lemmatizer import Lemmatizer
from collections import defaultdict


class GlinerProcessorNER:
    def __init__(self, ner_model_path: str | GLiNER = "urchade/gliner_multi-v2.1"):
        if type(ner_model_path) == "str":
            self.ner = GLiNER.from_pretrained(ner_model_path)
        else:
            self.ner = ner_model_path

        self.person_labels = ["person"]
        self.location_labels = ["location", "room"]
        self.lemmatizer = Lemmatizer()

    
    def deduplicate_entities(self, entities: list[str], lemmatize: bool = False):
        raw_entities = list(set(entities))
        deduplicated_entities = []

        for entity in raw_entities:
            for candidate in raw_entities:
                if entity.lower() != candidate.lower() and entity.lower() in candidate.lower():
                    break
            else:
                if entity.lower() not in list(map(str.lower, deduplicated_entities)):
                    deduplicated_entities.append(entity)

        if lemmatize:
            deduplicated_entities = [entity for entity in deduplicated_entities if entity.lower() == self.lemmatizer.lemmatize(entity.lower())]
        
        return deduplicated_entities


    def extract_persons(self, text: str, lemmatize: bool = False):
        entities = self.ner.predict_entities(text, self.person_labels)

        entities = [entity["text"] for entity in entities]

        return {"persons": self.deduplicate_entities(entities, lemmatize=lemmatize)}
        

    def extract_locations(self, text: str, lemmatize: bool = False):
        entities = self.ner.predict_entities(text, self.location_labels)

        entities = [entity["text"] for entity in entities]

        return {"locations": self.deduplicate_entities(entities, lemmatize=lemmatize)}

    def extract_all(self, text: str, lemmatize: bool = False):
        entities = self.ner.predict_entities(text, self.person_labels + self.location_labels)

        typed_output = defaultdict(list)
        for entity in entities:
            if entity["label"] in self.location_labels:
                typed_output["locations"].append(entity["text"])
            else:
                typed_output["persons"].append(entity["text"])

        return {key: self.deduplicate_entities(value, lemmatize=lemmatize) for key, value in typed_output.items()}
