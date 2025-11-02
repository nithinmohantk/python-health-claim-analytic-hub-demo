"""
Network visualization module for HealthClaim Analytics Hub
Handles creation and visualization of patient-provider networks
"""

import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from typing import Tuple, Dict
import streamlit as st


def build_patient_provider_network(df: pd.DataFrame) -> nx.Graph:
    """
    Build a graph representing patient-provider relationships.
    
    Args:
        df: Claims DataFrame with patient_id and provider_id columns
        
    Returns:
        NetworkX Graph object
    """
    G = nx.Graph()
    
    for _, row in df.iterrows():
        # Handle both numeric IDs and UUID strings
        patient_id = row['patient_id']
        provider_id = row['provider_id']
        
        # Convert to string for node naming (works for both int and UUID)
        try:
            patient_node = f"Patient_{int(patient_id)}"
        except (ValueError, TypeError):
            # If it's a UUID or non-numeric string, use it directly
            patient_node = f"Patient_{str(patient_id)[:8]}"  # Use first 8 chars of UUID
        
        try:
            provider_node = f"Provider_{int(provider_id)}"
        except (ValueError, TypeError):
            # If it's a UUID or non-numeric string, use it directly
            provider_node = f"Provider_{str(provider_id)[:8]}"  # Use first 8 chars of UUID
        
        # Add nodes with type attribute
        G.add_node(patient_node, node_type='patient')
        G.add_node(provider_node, node_type='provider')
        
        # Add edge with claim amount as weight
        claim_amount = float(row['claim_amount'])
        if G.has_edge(patient_node, provider_node):
            # If edge exists, increment the weight
            G[patient_node][provider_node]['claim_amount'] += claim_amount
            G[patient_node][provider_node]['count'] += 1
        else:
            G.add_edge(patient_node, provider_node, 
                      claim_amount=claim_amount, count=1)
    
    return G


def create_network_visualization(
    G: nx.Graph,
    node_size_scale: float = 1.0,
    edge_width_scale: float = 1.0,
    title: str = "Patient-Provider Network"
) -> go.Figure:
    """
    Create an interactive Plotly visualization of the network.
    
    Args:
        G: NetworkX Graph object
        node_size_scale: Scale factor for node sizes
        edge_width_scale: Scale factor for edge widths
        title: Title for the visualization
        
    Returns:
        Plotly Figure object
    """
    # Calculate layout
    pos = nx.spring_layout(G, k=0.2, iterations=50, seed=42)
    
    # Extract edge information
    edge_x = []
    edge_y = []
    edge_weights = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        # Store weight for tooltip
        edge_weights.append(edge[2].get('claim_amount', 0))
    
    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=0.5 * edge_width_scale, color='#888'),
        hoverinfo='none',
        showlegend=False
    )
    
    # Extract node information
    node_x = []
    node_y = []
    node_color = []
    node_size = []
    node_text = []
    node_degree = dict(G.degree())
    
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        
        # Color by node type
        if node[1]['node_type'] == 'patient':
            node_color.append('#1f77b4')  # Blue for patients
        else:
            node_color.append('#ff7f0e')  # Orange for providers
        
        # Size by degree (number of connections)
        degree = node_degree[node[0]]
        node_size.append(10 + degree * 2 * node_size_scale)
        
        # Hover text with connection count
        node_text.append(f"{node[0]}<br>Connections: {degree}")
    
    # Create node trace
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[node.split('_')[0] + '<br>' + node.split('_')[1] for node in G.nodes()],
        textposition='top center',
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            title_x=0.5,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=700
        )
    )
    
    return fig


def get_network_statistics(G: nx.Graph) -> Dict:
    """
    Calculate network statistics.
    
    Args:
        G: NetworkX Graph object
        
    Returns:
        Dictionary of network statistics
    """
    # Always return a dict with default values
    num_nodes = G.number_of_nodes()
    
    if num_nodes == 0:
        return {
            'num_nodes': 0,
            'num_edges': 0,
            'avg_degree': 0.0,
            'density': 0.0,
            'num_connected_components': 0,
            'is_connected': False,
        }
    
    return {
        'num_nodes': num_nodes,
        'num_edges': G.number_of_edges(),
        'avg_degree': sum(dict(G.degree()).values()) / num_nodes,
        'density': nx.density(G),
        'num_connected_components': nx.number_connected_components(G),
        'is_connected': nx.is_connected(G),
    }


def detect_suspicious_clusters(G: nx.Graph, min_cluster_size: int = 3) -> Dict:
    """
    Detect potentially suspicious patient-provider clusters.
    
    Args:
        G: NetworkX Graph object
        min_cluster_size: Minimum size to consider as suspicious
        
    Returns:
        Dictionary with cluster information
    """
    # Find cliques (fully connected subgraphs)
    cliques = list(nx.find_cliques(G))
    
    # Filter by size
    suspicious_cliques = [c for c in cliques if len(c) >= min_cluster_size]
    
    return {
        'total_cliques': len(cliques),
        'suspicious_cliques': len(suspicious_cliques),
        'clique_details': suspicious_cliques[:10]  # Top 10 for display
    }
