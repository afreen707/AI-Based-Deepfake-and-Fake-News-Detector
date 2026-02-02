# Wrapper for fake news detection
# fake_news_model.py
import os
import re

class FakeNewsModel:
    def __init__(self):
        self.model_path = os.path.join('models', 'saved_models', 'fake_news_bert')
        print(f"Fake News Model initialized from {self.model_path}")
        
        # Clickbait keywords
        self.clickbait_keywords = [
            'shocking', 'unbelievable', 'you won\'t believe', 'click here',
            'amazing', 'incredible', 'must see', 'one weird trick',
            'they don\'t want you to know', 'revealed', 'exposed'
        ]
        
        # Conspiracy theory indicators
        self.conspiracy_keywords = [
            'controlled', 'control the population', 'new world order',
            'illuminati', 'deep state', 'cover up', 'they don\'t want',
            'wake up', 'sheeple', 'planned', 'orchestrated',
            'false flag', 'crisis actor', 'hoax', 'plandemic',
            'big pharma', 'government lie', 'mainstream media lies'
        ]
        
        # Medical misinformation patterns
        self.medical_misinfo = [
            'created in a lab', 'laboratory', 'bioweapon', 'man-made virus',
            'microchip', '5g causes', 'vaccine contains', 'poison',
            'depopulation', 'tracking device', 'mind control'
        ]
        
        # Unverified claim patterns
        self.unverified_patterns = [
            r'\b(secret|hidden|suppressed)\s+(cure|treatment|evidence)\b',
            r'\b(doctors|scientists)\s+(don\'t want|hide|suppress)\b',
            r'\b(proof|evidence)\s+that\s+\w+\s+(created|planned|orchestrated)\b',
            r'\bwas\s+created\s+(by|in|to)\b',
        ]
        
        # Clickbait patterns
        self.clickbait_patterns = [
            r'\b(WON\'T BELIEVE|SHOCKED|STUNNED)\b',
            r'\b(BREAKING|URGENT|ALERT)\b',
            r'!!!+',
            r'\bCLICK HERE\b',
        ]

    def predict(self, text):
        """
        Input: text string
        Output: score (0-100), suspicious_phrases list
        """
        if not text or text.strip() == '':
            return 50, ["No text provided"]
        
        text_lower = text.lower()
        found_phrases = []
        suspicion_points = 0
        
        # 1. Check for clickbait keywords
        for keyword in self.clickbait_keywords:
            if keyword.lower() in text_lower:
                found_phrases.append(f"clickbait: {keyword}")
                suspicion_points += 8
        
        # 2. Check for conspiracy theory keywords
        for keyword in self.conspiracy_keywords:
            if keyword.lower() in text_lower:
                found_phrases.append(f"conspiracy indicator: {keyword}")
                suspicion_points += 15
        
        # 3. Check for medical misinformation
        for keyword in self.medical_misinfo:
            if keyword.lower() in text_lower:
                found_phrases.append(f"medical misinfo: {keyword}")
                suspicion_points += 20
        
        # 4. Check for unverified claim patterns
        for pattern in self.unverified_patterns:
            if re.search(pattern, text_lower):
                found_phrases.append("unverified claim pattern")
                suspicion_points += 18
        
        # 5. Check for clickbait patterns
        for pattern in self.clickbait_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_phrases.append("clickbait formatting")
                suspicion_points += 10
        
        # 6. Check for ALL CAPS (more than 30% of text)
        if len(text) > 0:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.3:
                found_phrases.append("excessive capitalization")
                suspicion_points += 10
        
        # 7. Check for excessive punctuation
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            found_phrases.append("excessive exclamation marks")
            suspicion_points += 8
        
        # 8. Check for lack of sources (simplified check)
        has_source = any(indicator in text_lower for indicator in [
            'according to', 'study shows', 'research', 'published in',
            'http://', 'https://', 'source:', 'report', 'journal'
        ])
        
        # If making strong claims without sources
        strong_claims = any(word in text_lower for word in [
            'was created', 'is proven', 'definitely', 'certainly', 'fact that'
        ])
        
        if strong_claims and not has_source:
            found_phrases.append("strong claims without cited sources")
            suspicion_points += 12
        
        # 9. Check for emotional manipulation
        emotional_words = ['fear', 'scared', 'terrified', 'panic', 'threat', 'danger']
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        if emotional_count >= 2:
            found_phrases.append("emotional manipulation language")
            suspicion_points += 10
        
        # Calculate credibility score (higher is more credible)
        score = max(0, min(100, 100 - suspicion_points))
        
        # Remove duplicates
        found_phrases = list(set(found_phrases))
        
        # If no issues found, give high credibility
        if not found_phrases:
            found_phrases = ["No suspicious patterns detected"]
            score = 95
        
        return score, found_phrases