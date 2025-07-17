import spacy
import re
from typing import List, Dict, Any, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class CVAnalyzer:
    def __init__(self):
        try:
            # Load Portuguese spaCy model (fallback to English if not available)
            try:
                self.nlp = spacy.load("pt_core_news_sm")
            except OSError:
                logger.warning("Portuguese model not found, using English model")
                self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("No spaCy model found. Please install: python -m spacy download pt_core_news_sm")
            self.nlp = None
        
        # Define action verbs for CV improvement
        self.action_verbs = {
            'pt': [
                'desenvolvi', 'criei', 'implementei', 'geri', 'liderei', 'coordenei',
                'otimizei', 'melhorei', 'aumentei', 'reduzi', 'alcancei', 'realizei',
                'estabeleci', 'construí', 'projetei', 'executei', 'supervisionei',
                'colaborei', 'inovei', 'transformei', 'automatizei', 'analisei'
            ],
            'en': [
                'developed', 'created', 'implemented', 'managed', 'led', 'coordinated',
                'optimized', 'improved', 'increased', 'reduced', 'achieved', 'accomplished',
                'established', 'built', 'designed', 'executed', 'supervised',
                'collaborated', 'innovated', 'transformed', 'automated', 'analyzed'
            ]
        }
        
        # Weak words to avoid
        self.weak_words = {
            'pt': ['responsável por', 'ajudei', 'participei', 'trabalhei em', 'fiz parte'],
            'en': ['responsible for', 'helped', 'participated', 'worked on', 'was part of']
        }
        
        # Professional sectors keywords
        self.sector_keywords = {
            'tecnologia': ['python', 'java', 'javascript', 'react', 'angular', 'node.js', 'sql', 'mongodb', 'aws', 'docker', 'kubernetes'],
            'marketing': ['seo', 'sem', 'google analytics', 'facebook ads', 'content marketing', 'social media', 'branding'],
            'vendas': ['crm', 'salesforce', 'pipeline', 'leads', 'conversão', 'negociação', 'b2b', 'b2c'],
            'recursos_humanos': ['recrutamento', 'seleção', 'treinamento', 'desenvolvimento', 'performance', 'cultura organizacional'],
            'financas': ['excel', 'power bi', 'análise financeira', 'orçamento', 'fluxo de caixa', 'investimentos', 'contabilidade']
        }

    def analyze_cv(self, cv_text: str, sector: str = None) -> Dict[str, Any]:
        """Analyze CV and provide suggestions for improvement."""
        if not self.nlp:
            return self._basic_analysis(cv_text, sector)
        
        doc = self.nlp(cv_text)
        
        # Perform various analyses
        score = self._calculate_score(cv_text, doc)
        suggestions = self._generate_suggestions(cv_text, doc, sector)
        keywords = self._extract_keywords(doc, sector)
        improved_text = self._suggest_improvements(cv_text)
        
        return {
            'analyzed_text': improved_text,
            'suggestions': suggestions,
            'analysis_score': score,
            'keywords': keywords,
            'word_count': len(doc),
            'sentence_count': len(list(doc.sents))
        }

    def _calculate_score(self, text: str, doc) -> int:
        """Calculate CV quality score (0-100)."""
        score = 50  # Base score
        
        # Check for action verbs
        action_verb_count = self._count_action_verbs(text)
        score += min(action_verb_count * 5, 20)
        
        # Check for weak words (penalty)
        weak_word_count = self._count_weak_words(text)
        score -= min(weak_word_count * 3, 15)
        
        # Check for quantifiable results
        numbers = re.findall(r'\d+%|\d+\+|€\d+|\$\d+|\d+k|\d+ anos?|\d+ meses?', text.lower())
        score += min(len(numbers) * 3, 15)
        
        # Check length (optimal range)
        word_count = len(doc)
        if 200 <= word_count <= 800:
            score += 10
        elif word_count < 200:
            score -= 10
        elif word_count > 1000:
            score -= 5
        
        # Check for contact information
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 5
        if re.search(r'\+?[\d\s\-\(\)]{9,}', text):
            score += 5
        
        return max(0, min(100, score))

    def _generate_suggestions(self, text: str, doc, sector: str = None) -> List[Dict[str, Any]]:
        """Generate specific suggestions for CV improvement."""
        suggestions = []
        
        # Check for action verbs
        action_verb_count = self._count_action_verbs(text)
        if action_verb_count < 3:
            suggestions.append({
                'type': 'action_verbs',
                'priority': 'high',
                'title': 'Use mais verbos de ação',
                'description': 'Substitua frases passivas por verbos de ação como "desenvolvi", "implementei", "geri".',
                'examples': ['Em vez de "responsável por vendas" → "Geri equipa de vendas"']
            })
        
        # Check for quantifiable results
        numbers = re.findall(r'\d+%|\d+\+|€\d+|\$\d+|\d+k|\d+ anos?|\d+ meses?', text.lower())
        if len(numbers) < 2:
            suggestions.append({
                'type': 'quantifiable_results',
                'priority': 'high',
                'title': 'Adicione resultados quantificáveis',
                'description': 'Inclua números, percentagens e métricas para demonstrar o seu impacto.',
                'examples': ['Em vez de "melhorei as vendas" → "Aumentei as vendas em 25%"']
            })
        
        # Check for weak words
        weak_word_count = self._count_weak_words(text)
        if weak_word_count > 2:
            suggestions.append({
                'type': 'weak_words',
                'priority': 'medium',
                'title': 'Evite palavras fracas',
                'description': 'Substitua expressões vagas por verbos de ação específicos.',
                'examples': ['Em vez de "ajudei com" → "Coordenei" ou "Implementei"']
            })
        
        # Check word count
        word_count = len(doc)
        if word_count < 200:
            suggestions.append({
                'type': 'length',
                'priority': 'medium',
                'title': 'CV muito curto',
                'description': 'Adicione mais detalhes sobre as suas experiências e competências.',
                'examples': ['Inclua projetos específicos, tecnologias utilizadas, resultados alcançados']
            })
        elif word_count > 1000:
            suggestions.append({
                'type': 'length',
                'priority': 'low',
                'title': 'CV muito longo',
                'description': 'Considere resumir informações menos relevantes.',
                'examples': ['Foque nas experiências mais recentes e relevantes']
            })
        
        # Sector-specific suggestions
        if sector and sector in self.sector_keywords:
            sector_words = self.sector_keywords[sector]
            found_keywords = [word for word in sector_words if word.lower() in text.lower()]
            if len(found_keywords) < 3:
                suggestions.append({
                    'type': 'sector_keywords',
                    'priority': 'medium',
                    'title': f'Adicione palavras-chave de {sector}',
                    'description': f'Inclua mais termos técnicos relevantes para a área de {sector}.',
                    'examples': [f'Considere incluir: {", ".join(sector_words[:5])}']
                })
        
        return suggestions

    def _extract_keywords(self, doc, sector: str = None) -> List[str]:
        """Extract relevant keywords from CV."""
        keywords = []
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'LANGUAGE']:
                keywords.append(ent.text.lower())
        
        # Extract technical terms (nouns that might be technologies)
        for token in doc:
            if (token.pos_ == 'NOUN' and 
                len(token.text) > 3 and 
                not token.is_stop and 
                not token.is_punct):
                keywords.append(token.text.lower())
        
        # Add sector-specific keywords if found
        if sector and sector in self.sector_keywords:
            sector_words = self.sector_keywords[sector]
            found_sector_keywords = [word for word in sector_words if word.lower() in doc.text.lower()]
            keywords.extend(found_sector_keywords)
        
        # Remove duplicates and return most common
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(20)]

    def _suggest_improvements(self, text: str) -> str:
        """Suggest improved version of CV text."""
        improved_text = text
        
        # Replace weak phrases with stronger alternatives
        replacements = {
            'responsável por': 'geri',
            'ajudei com': 'colaborei em',
            'trabalhei em': 'desenvolvi',
            'participei em': 'contribuí para',
            'fiz parte de': 'integrei'
        }
        
        for weak, strong in replacements.items():
            improved_text = re.sub(weak, strong, improved_text, flags=re.IGNORECASE)
        
        return improved_text

    def _count_action_verbs(self, text: str) -> int:
        """Count action verbs in text."""
        text_lower = text.lower()
        count = 0
        for verb_list in self.action_verbs.values():
            for verb in verb_list:
                count += len(re.findall(r'\b' + verb + r'\b', text_lower))
        return count

    def _count_weak_words(self, text: str) -> int:
        """Count weak words/phrases in text."""
        text_lower = text.lower()
        count = 0
        for weak_list in self.weak_words.values():
            for weak in weak_list:
                count += len(re.findall(r'\b' + weak + r'\b', text_lower))
        return count

    def _basic_analysis(self, text: str, sector: str = None) -> Dict[str, Any]:
        """Basic analysis when spaCy is not available."""
        words = text.split()
        sentences = text.split('.')
        
        score = 50
        if len(words) > 100:
            score += 10
        if '@' in text:
            score += 10
        
        suggestions = [{
            'type': 'basic',
            'priority': 'medium',
            'title': 'Análise básica',
            'description': 'Para uma análise mais detalhada, instale o modelo spaCy português.',
            'examples': ['pip install spacy && python -m spacy download pt_core_news_sm']
        }]
        
        return {
            'analyzed_text': text,
            'suggestions': suggestions,
            'analysis_score': score,
            'keywords': [],
            'word_count': len(words),
            'sentence_count': len(sentences)
        }
