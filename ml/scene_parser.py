import re
from typing import List, Dict, Tuple, Optional
from ner.gliner_processor import GlinerProcessorNER


def parse_scenes(text: str) -> List[Dict[str, str]]:
    """
    Parse scenes from text using improved heuristics based on the actual format.
    
    Args:
        text (str): Full text extracted from PDF
        
    Returns:
        List[Dict[str, str]]: List of scenes with 'header' and 'content' keys
    """
    # Split text into lines
    lines = text.split('\n')
    
    scenes = []
    current_scene = None
    current_content = []
    code_pattern = r'^\d+(?:-\d+)*-?.?'
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()  # Keep leading spaces for content formatting
        
        # Check if line is a scene header
        if _is_scene_header(line):
            # If we already have a scene, save it
            if current_scene is not None:
                scenes.append({
                    'header': re.sub(code_pattern, "", current_scene).lstrip(),
                    'content': '\n'.join(current_content).strip()
                })
            
            # Collect all lines until the first blank line (header section)
            header_lines = []
            j = i
            while j < len(lines):
                header_line = lines[j].rstrip()
                # Stop at first blank line
                if not header_line.strip():
                    break
                header_lines.append(header_line)
                j += 1
            
            # Start new scene with complete header
            current_scene = '\n'.join(header_lines).strip()
            current_content = []
            i = j  # Skip to after the blank line
            continue
        elif current_scene is not None:
            # Add line to current scene content
            current_content.append(line)
        
        i += 1
    
    # Don't forget the last scene
    if current_scene is not None:
        scenes.append({
            'header': re.sub(code_pattern, "", current_scene).lstrip(),
            'content': '\n'.join(current_content).strip()
        })
    
    return scenes


def _normalize_time(time_text: str) -> str:
    """
    Normalize time text to standard English values.
    
    Args:
        time_text (str): Time text to normalize
        
    Returns:
        str: Normalized time
    """
    # Convert to uppercase for comparison
    time_upper = time_text.upper()
    
    # Russian to English mappings
    time_mapping = {
        'ДЕНЬ': 'DAY',
        'НОЧЬ': 'NIGHT',
        'УТРО': 'MORNING',
        'ВЕЧЕР': 'EVENING',
        'DAY': 'DAY',
        'NIGHT': 'NIGHT',
        'MORNING': 'MORNING',
        'EVENING': 'EVENING'
    }
    
    # Check for direct matches
    for key, value in time_mapping.items():
        if key in time_upper:
            return value
    
    # Handle partial matches
    if 'ДЕНЬ' in time_upper or 'DAY' in time_upper:
        return 'DAY'
    elif 'НОЧЬ' in time_upper or 'NIGHT' in time_upper:
        return 'NIGHT'
    elif 'УТРО' in time_upper or 'MORNING' in time_upper:
        return 'MORNING'
    elif 'ВЕЧЕР' in time_upper or 'EVENING' in time_upper:
        return 'EVENING'
    
    return time_text  # Return original if no match


def _is_scene_header(line: str) -> bool:
    """
    Check if a line is a scene header based on the actual format in the PDFs.
    
    Scene headers in the PDFs have these characteristics:
    - Start with a number followed by a space and INT./EXT.
    - Or start with INT./EXT. directly
    - Usually contain location and time information
    - Are typically short and distinct from dialogue/action
    """
    line = line.strip()
    if not line:
        return False
    
    # Skip simple page/scene numbers
    if re.match(r'^\d+\s*$', line):
        return False
    
    # Pattern for numbered scene headers: number followed by INT./EXT.
    numbered_pattern = r'^\d+\s*[.:]?\s*(?:\d+\s*[.:]?\s*)?(?:ИНТ|ЭКСТ|INT|EXT|НАТ)'
    
    # Pattern for unnumbered scene headers: starting directly with INT./EXT.
    unnumbered_pattern = r'(ИНТ|ЭКСТ|INT|EXT|НАТ)'
    
    # Check if line matches scene header patterns
    if re.findall(numbered_pattern, line) or re.findall(unnumbered_pattern, line):
        return True
    
    # Additional check for lines with location and time but no INT/EXT
    location_time_pattern = r'^\d+\s*[.:]?\s*\d*\s*[.:]?\s*[A-ZА-Я0-9].*(?:ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР|DAY|NIGHT|MORNING|EVENING)'
    if re.match(location_time_pattern, line):
        return True
    
    return False


class HeaderParser:
    def __init__(self, ner_model: GlinerProcessorNER):
        self.ner_model = ner_model

    def parse_scene_header(self, header_text: str, lemmatize: bool = False) -> Dict:
        output = {}
        output["slugline_raw"] = header_text.strip()
        
        # Extract type (INT/EXT) - normalize Russian to English
        type_pattern = r'(ИНТ|ЭКСТ|INT|EXT|НАТ|NAT)'
        type_match = re.search(type_pattern, header_text, re.IGNORECASE)
        if type_match:
            type_raw = type_match.group(1).upper()
            # Normalize Russian to English
            if type_raw in ['ИНТ', 'INT']:
                output["type"] = "INT"
            elif type_raw in ['ЭКСТ', 'EXT']:
                output["type"] = "EXT"
            elif type_raw in ['НАТ', 'NAT']:
                output["type"] = "NAT"
        else:
            output["type"] = None

        header_text = re.sub(type_pattern, "", header_text)

        time_pattern = r'\b(?:ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР|DAY|NIGHT|MORNING|EVENING)\b'
        time_match = re.search(time_pattern, header_text, re.IGNORECASE)

        if time_match:
            time_start = time_match.start()
            time_end = time_match.end()
            time_text = header_text[time_start:time_end].strip()
            time_text = _normalize_time(time_text)
            header_text = re.sub(time_pattern, "", header_text)
        else:
            time_text = ""

        output["time"] = time_text

        ner_parsing = self.ner_model.extract_all(header_text, lemmatize=lemmatize)
        output["location"] = ner_parsing["locations"]
        output["persons"] = ner_parsing["persons"]

        return output


class ContentParser:
    def __init__(self, ner_model: GlinerProcessorNER):
        self.ner_model = ner_model

    def parse_scene_content(self, content_text: str, lemmatize: bool = False) -> Dict:
        output = {}
        output["content_raw"] = content_text.strip()

        # Use the ner_model to extract persons
        ner_parsing = self.ner_model.extract_persons(content_text, lemmatize=lemmatize)
        output["persons"] = ner_parsing.get("persons", [])

        return output


class TextParser:
    def __init__(self, ner_model: GlinerProcessorNER):
        self.ner_model = ner_model
        self.header_parser = HeaderParser(ner_model)
        self.content_parser = ContentParser(ner_model)

    
    @staticmethod
    def deduplicate_entities(entities: list[str]) -> list[str]:
        raw_entities = list(set(entities))
        deduplicated_entities = []

        for entity in raw_entities:
            for candidate in raw_entities:
                if entity.lower() != candidate.lower() and entity.lower() in candidate.lower():
                    break
            else:
                if entity.lower() not in list(map(str.lower, deduplicated_entities)):
                    deduplicated_entities.append(entity)

        return deduplicated_entities


    def parse_text(self, text_dict: Dict, lemmatize_header: bool = False, lemmatize_content: bool = True) -> Dict:
        output = {}
        header_text = text_dict.get("header", "")
        content_text = text_dict.get("content", "")

        # Parse header and content separately
        header_result = self.header_parser.parse_scene_header(header_text, lemmatize=lemmatize_header)
        content_result = self.content_parser.parse_scene_content(content_text, lemmatize=lemmatize_content)

        # Merge persons from both header and content, preserving order and removing duplicates
        persons_header = header_result.get("persons", [])
        persons_content = content_result.get("persons", [])

        # Use dict.fromkeys to preserve order and remove duplicates
        merged_persons = list(dict.fromkeys(persons_header + persons_content))

        # Compose result
        output.update(header_result)
        output.update({"content_raw": content_result.get("content_raw", "")})
        output["persons"] = self.deduplicate_entities(merged_persons)

        return output


