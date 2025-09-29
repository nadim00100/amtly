from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from config import Config


class LanguageService:
    """Language detection service - CLEANED VERSION"""

    def __init__(self):
        DetectorFactory.seed = 0
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.default_language = Config.DEFAULT_LANGUAGE
        self.language_names = Config.LANGUAGE_NAMES

    def detect_language(self, text, context=None):
        """
        Detect language from text with context awareness
        Returns: (language_code, confidence, reason)
        """
        if not text or not text.strip():
            return self.default_language, 'low', 'empty_text'

        cleaned_text = self._clean_text_for_detection(text)

        # Check for explicit language indicators first
        explicit_lang = self._detect_explicit_language(text, context)
        if explicit_lang:
            return explicit_lang, 'high', 'explicit_indicator'

        # Use keyword-based detection for short texts
        if len(cleaned_text) < 20:
            return self._detect_from_keywords(cleaned_text)

        # Use langdetect for longer texts
        try:
            detected_lang = detect(cleaned_text)
            confidence = 'high' if len(cleaned_text) > 50 else 'medium'

            if detected_lang in self.supported_languages:
                return detected_lang, confidence, 'langdetect'
            else:
                return self._detect_from_keywords(cleaned_text)

        except LangDetectException:
            return self._detect_from_keywords(cleaned_text)

    def _clean_text_for_detection(self, text):
        """Clean text to improve detection accuracy"""
        import re
        cleaned = re.sub(r'\b(form|HA|WBA|UF|KDU|VM|EK)\b', '', text, flags=re.IGNORECASE)
        cleaned = re.sub(r'\d+', '', cleaned)
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _detect_explicit_language(self, text, context=None):
        """Check for explicit language indicators"""
        text_lower = text.lower()

        # Language switching commands
        if any(phrase in text_lower for phrase in ['in english', 'auf englisch', 'translate to english']):
            return 'en'
        if any(phrase in text_lower for phrase in ['auf deutsch', 'in german', 'translate to german']):
            return 'de'

        # German institution requests (should be German)
        german_institutions = [
            'jobcenter', 'arbeitsagentur', 'sozialamt', 'bürgeramt',
            'krankenkasse', 'finanzamt', 'ausländerbehörde'
        ]
        if any(inst in text_lower for inst in german_institutions):
            if any(comm in text_lower for comm in ['email', 'brief', 'schreiben', 'write']):
                return 'de'

        return None

    def _detect_from_keywords(self, text):
        """Fallback: detect language from common keywords"""
        text_lower = text.lower()

        # German keywords
        german_keywords = [
            'bürgergeld', 'antrag', 'jobcenter', 'formular', 'hilfe', 'dokument',
            'beantragen', 'ausfüllen', 'frage', 'abschnitt', 'bescheid', 'behörde',
            'das', 'die', 'der', 'ist', 'und', 'mit', 'von', 'zu', 'auf', 'für',
            'was', 'wie', 'wo', 'wann', 'warum', 'welche', 'können', 'möchte',
            'bitte', 'danke', 'hallo', 'übersetzen', 'erklären', 'ich', 'bin'
        ]

        # English keywords
        english_keywords = [
            'help', 'form', 'application', 'document', 'translate', 'email',
            'write', 'explain', 'question', 'section', 'unemployment', 'benefit',
            'the', 'and', 'is', 'to', 'of', 'in', 'for', 'with', 'on', 'at',
            'what', 'how', 'where', 'when', 'why', 'which', 'can', 'would',
            'please', 'thank', 'hello', 'i', 'am', 'have', 'will'
        ]

        german_count = sum(1 for word in german_keywords if word in text_lower)
        english_count = sum(1 for word in english_keywords if word in text_lower)
        total_words = len(text_lower.split())

        german_ratio = german_count / max(total_words, 1)
        english_ratio = english_count / max(total_words, 1)

        if german_ratio > english_ratio and german_count >= 1:
            confidence = 'high' if german_count >= 3 else 'medium'
            return 'de', confidence, 'keyword_detection'
        elif english_count >= 1:
            confidence = 'high' if english_count >= 3 else 'medium'
            return 'en', confidence, 'keyword_detection'

        return self.default_language, 'low', 'fallback'

    def get_response_language(self, user_message, context=None):
        """Get the appropriate language for AI response - SIMPLIFIED"""
        detected_lang, confidence, reason = self.detect_language(user_message, context)

        # For high confidence or explicit indicators, use detected language
        if confidence in ['high'] or reason == 'explicit_indicator':
            return detected_lang

        # For medium confidence with supported language
        if confidence == 'medium' and detected_lang in self.supported_languages:
            return detected_lang

        return self.default_language

    def get_system_prompt_instruction(self, language_code, confidence='medium'):
        """Get instruction for AI to respond in specific language"""
        if language_code == 'de':
            if confidence == 'high':
                return "WICHTIG: Der Benutzer schreibt auf Deutsch. Antworte NUR auf Deutsch."
            else:
                return "Der Benutzer schreibt wahrscheinlich auf Deutsch. Antworte bitte auf Deutsch."
        else:  # English
            if confidence == 'high':
                return "IMPORTANT: The user is writing in English. Respond ONLY in English."
            else:
                return "The user appears to be writing in English. Please respond in English."

    def get_language_name(self, lang_code):
        """Get human-readable language name"""
        return self.language_names.get(lang_code, lang_code.upper())

    def is_german_institution_request(self, message):
        """Check if user is requesting communication with German institutions"""
        if not message:
            return False

        message_lower = message.lower()

        german_institutions = [
            'jobcenter', 'arbeitsagentur', 'agentur für arbeit', 'bundesagentur',
            'sozialamt', 'bürgeramt', 'amt', 'behörde', 'krankenkasse', 'finanzamt',
            'ausländerbehörde', 'einwohnermeldeamt', 'jugendamt', 'familienkasse',
            'rentenversicherung', 'berufsgenossenschaft', 'arbeitsamt'
        ]

        communication_words = [
            'email', 'e-mail', 'brief', 'letter', 'anschreiben', 'schreiben',
            'nachricht', 'message', 'write', 'schreib'
        ]

        has_institution = any(inst in message_lower for inst in german_institutions)
        has_communication = any(comm in message_lower for comm in communication_words)

        return has_institution and has_communication


# Create global instance
language_service = LanguageService()