"""
Unit tests for utils/network.py module

Tests network construction, visualization, and statistics
"""

import pytest
import networkx as nx
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.network import (
    build_patient_provider_network,
    get_network_statistics,
    detect_suspicious_clusters
)


class TestNetworkConstruction:
    """Tests for network construction"""
    
    def test_build_network_basic(self, sample_claims_df):
        """Test basic network construction"""
        G = build_patient_provider_network(sample_claims_df)
        assert isinstance(G, nx.Graph)
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() > 0
    
    def test_build_network_node_types(self, sample_claims_df):
        """Test that nodes have correct types"""
        G = build_patient_provider_network(sample_claims_df)
        
        for node, attrs in G.nodes(data=True):
            if 'Patient' in node:
                assert attrs.get('node_type') == 'patient'
            elif 'Provider' in node:
                assert attrs.get('node_type') == 'provider'
    
    def test_build_network_edge_weights(self, sample_claims_df):
        """Test that edge weights represent claim amounts"""
        G = build_patient_provider_network(sample_claims_df)
        
        for u, v, data in G.edges(data=True):
            assert 'claim_amount' in data
            assert data['claim_amount'] > 0
    
    def test_build_network_duplicate_edges(self):
        """Test that multiple claims between same patient-provider aggregate"""
        df = pd.DataFrame({
            'patient_id': [101, 101, 101],
            'provider_id': [501, 501, 502],
            'claim_amount': [1000, 500, 2000],
            'diagnosis_code': ['I10', 'I10', 'E11'],
        })
        G = build_patient_provider_network(df)
        
        # Patient_101 - Provider_501 edge should aggregate
        edge_data = G.get_edge_data("Patient_101", "Provider_501")
        assert edge_data['claim_amount'] == 1500
        assert edge_data['count'] == 2
    
    def test_build_network_empty_dataframe(self, empty_claims_df):
        """Test network construction with empty DataFrame"""
        G = build_patient_provider_network(empty_claims_df)
        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0


class TestNetworkStatistics:
    """Tests for network statistics calculation"""
    
    def test_network_statistics_basic(self, sample_network):
        """Test basic network statistics"""
        stats = get_network_statistics(sample_network)
        
        assert 'num_nodes' in stats
        assert 'num_edges' in stats
        assert 'avg_degree' in stats
        assert 'density' in stats
        assert 'num_connected_components' in stats
        assert 'is_connected' in stats
    
    def test_network_statistics_values(self, sample_network):
        """Test that statistics have correct values"""
        stats = get_network_statistics(sample_network)
        
        assert stats['num_nodes'] == 4
        assert stats['num_edges'] == 4
        assert stats['avg_degree'] > 0
        assert 0 <= stats['density'] <= 1
    
    def test_network_statistics_empty_graph(self):
        """Test statistics on empty graph"""
        G = nx.Graph()
        stats = get_network_statistics(G)
        # Empty graph should return default values, not empty dict
        assert stats['num_nodes'] == 0
        assert stats['num_edges'] == 0
        assert stats['avg_degree'] == 0.0
        assert stats['density'] == 0.0
    
    def test_network_connectivity(self, dense_network):
        """Test connectivity calculations"""
        stats = get_network_statistics(dense_network)
        
        assert stats['num_nodes'] > 0
        assert stats['num_edges'] > 0
        # Dense network should have multiple components
        assert stats['num_connected_components'] >= 1


class TestSuspiciousClusters:
    """Tests for suspicious cluster detection"""
    
    def test_detect_cliques_simple(self):
        """Test clique detection in simple graph"""
        G = nx.Graph()
        # Create a triangle (3-clique)
        G.add_edges_from([
            ("Patient_101", "Provider_501"),
            ("Patient_101", "Provider_502"),
            ("Provider_501", "Provider_502")
        ])
        
        clusters = detect_suspicious_clusters(G, min_cluster_size=3)
        assert clusters['total_cliques'] >= 1
    
    def test_detect_cliques_none(self, sample_network):
        """Test detection when no suspicious cliques exist"""
        clusters = detect_suspicious_clusters(sample_network, min_cluster_size=5)
        assert clusters['suspicious_cliques'] == 0
    
    def test_detect_cliques_returns_dict(self, sample_network):
        """Test that detection returns expected dictionary"""
        clusters = detect_suspicious_clusters(sample_network)
        
        assert 'total_cliques' in clusters
        assert 'suspicious_cliques' in clusters
        assert 'clique_details' in clusters
    
    def test_detect_cliques_size_filter(self, dense_network):
        """Test that clique size filter works"""
        clusters_small = detect_suspicious_clusters(dense_network, min_cluster_size=2)
        clusters_large = detect_suspicious_clusters(dense_network, min_cluster_size=5)
        
        assert clusters_small['suspicious_cliques'] >= clusters_large['suspicious_cliques']


class TestNetworkVisualization:
    """Tests for network visualization (without actual rendering)"""
    
    def test_visualization_components_exist(self, sample_network):
        """Test that visualization has required components"""
        from utils.network import create_network_visualization
        
        fig = create_network_visualization(sample_network)
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) >= 2  # Should have edge and node traces
    
    def test_visualization_node_colors(self, sample_network):
        """Test that visualization colors nodes correctly"""
        from utils.network import create_network_visualization
        
        fig = create_network_visualization(sample_network)
        
        # Node trace should be the second trace
        node_trace = fig.data[1]
        assert node_trace.marker.color is not None


class TestNetworkEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_single_patient_single_provider(self):
        """Test network with one patient and one provider"""
        df = pd.DataFrame({
            'patient_id': [101],
            'provider_id': [501],
            'claim_amount': [1000],
            'diagnosis_code': ['I10'],
        })
        G = build_patient_provider_network(df)
        
        assert G.number_of_nodes() == 2
        assert G.number_of_edges() == 1
    
    def test_large_network_construction(self, large_claims_df):
        """Test network construction with larger dataset"""
        G = build_patient_provider_network(large_claims_df)
        
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() > 0
        assert G.number_of_nodes() <= len(large_claims_df) * 2
    
    def test_network_with_self_loops(self):
        """Test that networks don't create self-loops"""
        df = pd.DataFrame({
            'patient_id': [101, 102],
            'provider_id': [101, 201],
            'claim_amount': [1000, 2000],
            'diagnosis_code': ['I10', 'E11'],
        })
        G = build_patient_provider_network(df)
        
        # Should not have self-loops
        assert not list(nx.selfloop_edges(G))


class TestNetworkIntegration:
    """Integration tests for network operations"""
    
    def test_construction_statistics_workflow(self, sample_claims_df):
        """Test workflow: construct network -> get statistics"""
        G = build_patient_provider_network(sample_claims_df)
        stats = get_network_statistics(G)
        
        assert stats['num_nodes'] > 0
        assert stats['num_edges'] > 0
    
    def test_construction_clustering_workflow(self, sample_claims_df):
        """Test workflow: construct network -> detect clusters"""
        G = build_patient_provider_network(sample_claims_df)
        clusters = detect_suspicious_clusters(G)
        
        assert isinstance(clusters, dict)
        assert 'suspicious_cliques' in clusters


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
