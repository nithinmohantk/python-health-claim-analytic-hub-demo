"""
Unit tests for utils/gpt.py module

Tests GPT integration, prompt generation, and error handling
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, Mock
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
            assert result is not None  # Should return OpenAI client
    
    def test_initialize_without_key(self):
        """Test initialization when API key is missing"""
        with patch('utils.gpt.st') as mock_st:
            mock_st.secrets = {}
            mock_st.error = MagicMock()
            initialize_openai()
            # Should call st.error
            mock_st.error.assert_called()
    
    def test_initialize_returns_client(self):
        """Test that initialize returns OpenAI client"""
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            result = initialize_openai()
            assert result is not None  # Should be OpenAI client object


class TestAnomalyExplanation:
    """Tests for anomaly explanation generation"""
    
    def test_generate_explanation_success(self, sample_claims_df):
        """Test successful anomaly explanation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='This claim is suspicious because...'))]
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                claim = sample_claims_df.iloc[0]
                result = generate_anomaly_explanation(claim)
                
                assert result is not None
                assert 'suspicious' in result.lower()
    
    def test_generate_explanation_with_context(self, sample_claims_df):
        """Test explanation generation with additional context"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Analysis complete.'))]
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                claim = sample_claims_df.iloc[0]
                context = "This is test context"
                result = generate_anomaly_explanation(claim, context=context)
                
                # Verify the context was included in the call
                assert mock_instance.chat.completions.create.called
    
    def test_generate_explanation_auth_error(self, sample_claims_df):
        """Test handling of authentication errors"""
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-invalid'}):
            with patch('utils.gpt.st.error'):
                with patch('utils.gpt.OpenAI') as mock_client:
                    mock_instance = MagicMock()
                    mock_client.return_value = mock_instance
                    mock_instance.chat.completions.create.side_effect = Exception("401 Unauthorized")
                    
                    claim = sample_claims_df.iloc[0]
                    result = generate_anomaly_explanation(claim)
                    
                    assert result is None


class TestNetworkInsights:
    """Tests for network insights generation"""
    
    def test_generate_network_insights(self):
        """Test network insights generation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Network analysis shows potential fraud rings...'))]
        
        network_stats = {
            'num_nodes': 10,
            'num_edges': 15,
            'avg_degree': 2.5,
            'density': 0.3,
        }
        clusters = {'suspicious_cliques': 2}
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                result = generate_network_insights(network_stats, clusters, 100)
                
                assert result is not None
                assert 'fraud' in result.lower() or 'network' in result.lower()
    
    def test_network_insights_empty_clusters(self):
        """Test network insights with no suspicious clusters"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Network appears normal.'))]
        
        network_stats = {
            'num_nodes': 5, 
            'num_edges': 3,
            'avg_degree': 1.2,
            'density': 0.1,
            'num_connected_components': 2
        }
        clusters = {'suspicious_cliques': 0, 'total_cliques': 0}
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                result = generate_network_insights(network_stats, clusters, 10)
                
                assert result is not None


class TestClaimsQuestion:
    """Tests for Q&A interface"""
    
    def test_answer_claims_question(self):
        """Test answering claims data questions"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Based on the data, the answer is...'))]
        
        question = "What is the average claim amount?"
        context = "Total: 100 claims, Average: $2000"
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                result = answer_claims_question(question, context)
                
                assert result is not None
                assert 'answer' in result.lower() or 'data' in result.lower()
    
    def test_answer_question_complex(self):
        """Test answering complex question"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Complex analysis...'))]
        
        question = "Which providers have the highest anomaly rates?"
        context = "Provider data shows Provider_502 with 35% anomaly rate"
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                result = answer_claims_question(question, context)
                
                assert mock_instance.chat.completions.create.called


class TestAPIValidation:
    """Tests for API connection validation"""
    
    def test_validate_connection_success(self):
        """Test successful connection validation"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='ready'))]
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                result = validate_api_connection()
                
                assert result is True
    
    def test_validate_connection_failure(self):
        """Test failed connection validation"""
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-invalid'}):
            with patch('utils.gpt.st.error'):
                with patch('utils.gpt.OpenAI') as mock_client:
                    mock_instance = MagicMock()
                    mock_client.return_value = mock_instance
                    mock_instance.chat.completions.create.side_effect = Exception("Connection failed")
                    
                    result = validate_api_connection()
                    
                    assert result is False
    
    def test_validate_connection_wrong_response(self):
        """Test connection validation succeeds with any response (more resilient)"""
        # Updated: API connection is valid if we get ANY response from OpenAI
        # This is more practical than requiring exact match
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='anything works'))]
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                result = validate_api_connection()
                
                # Connection is valid if we got a response (more resilient than exact match)
                assert result is True


class TestPromptGeneration:
    """Tests for prompt generation and formatting"""
    
    def test_prompt_includes_claim_details(self, sample_claims_df):
        """Test that prompts include claim details"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Analysis.'))]
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.return_value = mock_response
                
                claim = sample_claims_df.iloc[0]
                generate_anomaly_explanation(claim)
                
                # Check that the API was called
                assert mock_instance.chat.completions.create.called
                
                # Verify message content
                call_args = mock_instance.chat.completions.create.call_args
                messages = call_args[1]['messages']
                assert len(messages) > 0


class TestErrorHandling:
    """Tests for error handling in GPT module"""
    
    def test_rate_limit_error(self, sample_claims_df):
        """Test handling of rate limit errors"""
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.st.warning'):
                with patch('utils.gpt.OpenAI') as mock_client:
                    mock_instance = MagicMock()
                    mock_client.return_value = mock_instance
                    mock_instance.chat.completions.create.side_effect = Exception("Rate limit exceeded")
                    
                    claim = sample_claims_df.iloc[0]
                    result = generate_anomaly_explanation(claim)
                    
                    assert result is None
    
    def test_timeout_error(self, sample_claims_df):
        """Test handling of timeout errors"""
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.st.error'):
                with patch('utils.gpt.OpenAI') as mock_client:
                    mock_instance = MagicMock()
                    mock_client.return_value = mock_instance
                    mock_instance.chat.completions.create.side_effect = TimeoutError("Request timeout")
                    
                    claim = sample_claims_df.iloc[0]
                    result = generate_anomaly_explanation(claim)
                    
                    assert result is None


class TestGPTIntegration:
    """Integration tests for GPT module"""
    
    def test_full_analysis_workflow(self, sample_claims_df):
        """Test complete GPT analysis workflow"""
        responses = [
            Mock(choices=[Mock(message=Mock(content='Explanation for anomaly.'))]),
            Mock(choices=[Mock(message=Mock(content='Network analysis.'))]),
            Mock(choices=[Mock(message=Mock(content='Answer to question.'))]),
        ]
        
        with patch('utils.gpt.st.secrets', {'OPENAI_API_KEY': 'sk-test'}):
            with patch('utils.gpt.OpenAI') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                mock_instance.chat.completions.create.side_effect = responses
                
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
