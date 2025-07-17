import pytest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.services.cv_analyzer import CVAnalyzer

class TestCVAnalyzer:
    """Test cases for CV Analyzer service."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = CVAnalyzer()
    
    def test_basic_analysis(self):
        """Test basic CV analysis functionality."""
        cv_text = """
        Nome: João Silva
        Email: joao.silva@email.com
        
        Experiência:
        - Desenvolvi aplicações web em Python
        - Implementei APIs REST
        - Melhorei performance em 30%
        
        Competências:
        - Python, JavaScript, SQL
        """
        
        result = self.analyzer.analyze_cv(cv_text)
        
        assert 'analysis_score' in result
        assert 'suggestions' in result
        assert 'keywords' in result
        assert isinstance(result['analysis_score'], int)
        assert 0 <= result['analysis_score'] <= 100
    
    def test_action_verbs_detection(self):
        """Test action verbs detection."""
        text_with_action_verbs = "Desenvolvi, implementei e geri projetos importantes."
        count = self.analyzer._count_action_verbs(text_with_action_verbs)
        assert count > 0
    
    def test_weak_words_detection(self):
        """Test weak words detection."""
        text_with_weak_words = "Fui responsável por ajudar com projetos."
        count = self.analyzer._count_weak_words(text_with_weak_words)
        assert count > 0
    
    def test_sector_specific_analysis(self):
        """Test sector-specific analysis."""
        tech_cv = """
        Experiência em Python, Django, React, AWS.
        Desenvolvi aplicações web escaláveis.
        """
        
        result = self.analyzer.analyze_cv(tech_cv, sector="tecnologia")
        
        # Should have tech-related keywords
        keywords = result.get('keywords', [])
        tech_keywords = ['python', 'django', 'react', 'aws']
        found_tech_keywords = [k for k in keywords if k.lower() in tech_keywords]
        assert len(found_tech_keywords) > 0
    
    def test_score_calculation(self):
        """Test score calculation logic."""
        # High quality CV
        good_cv = """
        Nome: Maria Santos
        Email: maria@email.com
        Telefone: +351 123 456 789
        
        Desenvolvi 5 aplicações web que aumentaram a eficiência em 40%.
        Implementei sistemas que reduziram custos em €50,000.
        Geri equipa de 10 desenvolvedores durante 3 anos.
        """
        
        # Low quality CV
        poor_cv = """
        Trabalhei numa empresa.
        Fui responsável por algumas tarefas.
        Ajudei com projetos.
        """
        
        good_result = self.analyzer.analyze_cv(good_cv)
        poor_result = self.analyzer.analyze_cv(poor_cv)
        
        assert good_result['analysis_score'] > poor_result['analysis_score']
    
    def test_suggestions_generation(self):
        """Test suggestions generation."""
        cv_text = "Trabalhei numa empresa de tecnologia."
        
        result = self.analyzer.analyze_cv(cv_text)
        suggestions = result.get('suggestions', [])
        
        assert len(suggestions) > 0
        
        # Check suggestion structure
        for suggestion in suggestions:
            assert 'type' in suggestion
            assert 'priority' in suggestion
            assert 'title' in suggestion
            assert 'description' in suggestion
            assert suggestion['priority'] in ['high', 'medium', 'low']

if __name__ == "__main__":
    pytest.main([__file__])
