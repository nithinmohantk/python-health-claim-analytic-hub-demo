"""
Unit tests for utils/gpt.py module

Tests GPT integration, prompt generation, and error handling
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.gpt import (
    initialize_openai,
    generate_anomaly_explanation,
    generate_network_insights,
    answer_claims_question,
    validate_api_connection
)


class TestOpenAIInitialization:
    """Tests for OpenAI API initialization"""
    
    def test_initialize_with_key(self):
        """Test initialization when API key exists"""
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test-key'}):
            result = initialize_openai()
            assert result is True
    
    def test_initialize_without_key(self):
        """Test initialization when API key is missing"""
        with patch('utils.gpt.st') as mock_st:
            mock_st.secrets = {}
            mock_st.error = MagicMock()
            initialize_openai()
            # Should call st.error
            mock_st.error.assert_called()
    
    def test_initialize_returns_bool(self):
        """Test that initialize returns boolean"""
        with patch('utils.gpt.st') as mock_st:
            mock_st.secrets = {'OPENAI_API_KEY': 'sk-test'}
            result = initialize_openai()
            assert isinstance(result, bool)


class TestAnomalyExplanation:
    """Tests for anomaly explanation generation"""
    
    @patch('openai.ChatCompletion.create')
    def test_generate_explanation_success(self, mock_create, sample_claims_df):
        """Test successful anomaly explanation"""
        mock_response = {
            'choices': [{'message': {'content': 'This claim is suspicious because...'}}]
        }
        mock_create.return_value = mock_response
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                claim = sample_claims_df.iloc[0]
                result = generate_anomaly_explanation(claim)
                
                assert result is not None
                assert 'suspicious' in result.lower()
    
    @patch('openai.ChatCompletion.create')
    def test_generate_explanation_with_context(self, mock_create, sample_claims_df):
        """Test explanation generation with additional context"""
        mock_response = {
            'choices': [{'message': {'content': 'Analysis complete.'}}]
        }
        mock_create.return_value = mock_response
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                claim = sample_claims_df.iloc[0]
                context = "This is test context"
                result = generate_anomaly_explanation(claim, context=context)
                
                # Verify the context was included in the call
                assert mock_create.called
    
    @patch('openai.ChatCompletion.create')
    def test_generate_explanation_auth_error(self, mock_create, sample_claims_df):
        """Test handling of authentication errors"""
        mock_create.side_effect = Exception("401 Unauthorized")
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-invalid'}):
            with patch('utils.gpt.st.error'):
                claim = sample_claims_df.iloc[0]
                result = generate_anomaly_explanation(claim)
                
                assert result is None


class TestNetworkInsights:
    """Tests for network insights generation"""
    
    @patch('openai.ChatCompletion.create')
    def test_generate_network_insights(self, mock_create):
        """Test network insights generation"""
        mock_response = {
            'choices': [{'message': {'content': 'Network analysis shows potential fraud rings...'}}]
        }
        mock_create.return_value = mock_response
        
        network_stats = {
            'num_nodes': 10,
            'num_edges': 15,
            'avg_degree': 2.5,
            'density': 0.3,
        }
        clusters = {'suspicious_cliques': 2}
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                result = generate_network_insights(network_stats, clusters, 100)
                
                assert result is not None
                assert 'fraud' in result.lower() or 'network' in result.lower()
    
    @patch('openai.ChatCompletion.create')
    def test_network_insights_empty_clusters(self, mock_create):
        """Test network insights with no suspicious clusters"""
        mock_response = {
            'choices': [{'message': {'content': 'Network appears normal.'}}]
        }
        mock_create.return_value = mock_response
        
        network_stats = {
            'num_nodes': 5, 
            'num_edges': 3,
            'avg_degree': 1.2,
            'density': 0.1,
            'num_connected_components': 2
        }
        clusters = {'suspicious_cliques': 0, 'total_cliques': 0}
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                result = generate_network_insights(network_stats, clusters, 10)
                
                assert result is not None


class TestClaimsQuestion:
    """Tests for Q&A interface"""
    
    @patch('openai.ChatCompletion.create')
    def test_answer_claims_question(self, mock_create):
        """Test answering claims data questions"""
        mock_response = {
            'choices': [{'message': {'content': 'Based on the data, the answer is...'}}]
        }
        mock_create.return_value = mock_response
        
        question = "What is the average claim amount?"
        context = "Total: 100 claims, Average: $2000"
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                result = answer_claims_question(question, context)
                
                assert result is not None
                assert 'answer' in result.lower() or 'data' in result.lower()
    
    @patch('openai.ChatCompletion.create')
    def test_answer_question_complex(self, mock_create):
        """Test answering complex question"""
        mock_response = {
            'choices': [{'message': {'content': 'Complex analysis...'}}]
        }
        mock_create.return_value = mock_response
        
        question = "Which providers have the highest anomaly rates?"
        context = "Provider data shows Provider_502 with 35% anomaly rate"
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                result = answer_claims_question(question, context)
                
                assert mock_create.called


class TestAPIValidation:
    """Tests for API connection validation"""
    
    @patch('openai.ChatCompletion.create')
    def test_validate_connection_success(self, mock_create):
        """Test successful connection validation"""
        mock_response = {
            'choices': [{'message': {'content': 'ready'}}]
        }
        mock_create.return_value = mock_response
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                result = validate_api_connection()
                
                assert result is True
    
    @patch('openai.ChatCompletion.create')
    def test_validate_connection_failure(self, mock_create):
        """Test failed connection validation"""
        mock_create.side_effect = Exception("Connection failed")
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-invalid'}):
            with patch('utils.gpt.st.error'):
                result = validate_api_connection()
                
                assert result is False
    
    @patch('openai.ChatCompletion.create')
    def test_validate_connection_wrong_response(self, mock_create):
        """Test connection validation with unexpected response"""
        mock_response = {
            'choices': [{'message': {'content': 'not ready'}}]
        }
        mock_create.return_value = mock_response
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                result = validate_api_connection()
                
                assert result is False


class TestPromptGeneration:
    """Tests for prompt generation and formatting"""
    
    @patch('openai.ChatCompletion.create')
    def test_prompt_includes_claim_details(self, mock_create, sample_claims_df):
        """Test that prompts include claim details"""
        mock_response = {
            'choices': [{'message': {'content': 'Analysis.'}}]
        }
        mock_create.return_value = mock_response
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                claim = sample_claims_df.iloc[0]
                generate_anomaly_explanation(claim)
                
                # Check that the API was called
                assert mock_create.called
                
                # Verify message content
                call_args = mock_create.call_args
                messages = call_args[1]['messages']
                assert len(messages) > 0


class TestErrorHandling:
    """Tests for error handling in GPT module"""
    
    @patch('openai.ChatCompletion.create')
    def test_rate_limit_error(self, mock_create, sample_claims_df):
        """Test handling of rate limit errors"""
        mock_create.side_effect = Exception("Rate limit exceeded")
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.st.warning'):
                claim = sample_claims_df.iloc[0]
                result = generate_anomaly_explanation(claim)
                
                assert result is None
    
    @patch('openai.ChatCompletion.create')
    def test_timeout_error(self, mock_create, sample_claims_df):
        """Test handling of timeout errors"""
        mock_create.side_effect = TimeoutError("Request timeout")
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.st.error'):
                claim = sample_claims_df.iloc[0]
                result = generate_anomaly_explanation(claim)
                
                assert result is None


class TestGPTIntegration:
    """Integration tests for GPT module"""
    
    @patch('openai.ChatCompletion.create')
    def test_full_analysis_workflow(self, mock_create, sample_claims_df):
        """Test complete GPT analysis workflow"""
        responses = [
            {'choices': [{'message': {'content': 'Explanation for anomaly.'}}]},
            {'choices': [{'message': {'content': 'Network analysis.'}}]},
            {'choices': [{'message': {'content': 'Answer to question.'}}]},
        ]
        mock_create.side_effect = responses
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.openai.api_key', 'sk-test'):
                # Test explanation
                claim = sample_claims_df.iloc[0]
                result1 = generate_anomaly_explanation(claim)
                assert result1 is not None
                
                # Test network insights
                network_stats = {
                    'num_nodes': 5,
                    'num_edges': 3,
                    'avg_degree': 1.2,
                    'density': 0.1,
                    'num_connected_components': 2
                }
                clusters = {'suspicious_cliques': 0, 'total_cliques': 0}
                result2 = generate_network_insights(network_stats, clusters, 10)
                assert result2 is not None
                
                # Test Q&A
                result3 = answer_claims_question("What?", "Context")
                assert result3 is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
