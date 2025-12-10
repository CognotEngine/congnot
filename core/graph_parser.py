

import json
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class Node:
    
    id: str  
    type: str  
    inputs: Dict[str, Any]  
    outputs: Dict[str, Any] = field(default_factory=dict)  
    position: Optional[Dict[str, float]] = None  
    metadata: Optional[Dict[str, Any]] = None  

@dataclass
class Edge:
    
    id: str  
    source: str  
    source_output: str  
    target: str  
    target_input: str  

@dataclass
class Graph:
    
    nodes: Dict[str, Node] = field(default_factory=dict)  
    edges: Dict[str, Edge] = field(default_factory=dict)  
    
    def add_node(self, node: Node) -> None:
        
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge) -> None:
        
        self.edges[edge.id] = edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        
        return self.edges.get(edge_id)
    
    def get_edges_from_node(self, node_id: str) -> List[Edge]:
        
        return [edge for edge in self.edges.values() if edge.source == node_id]
    
    def get_edges_to_node(self, node_id: str) -> List[Edge]:
        
        return [edge for edge in self.edges.values() if edge.target == node_id]
    
    def get_node_inputs(self, node_id: str) -> Dict[str, Any]:
        
        node = self.get_node(node_id)
        return node.inputs if node else {}
    
    def get_node_outputs(self, node_id: str) -> Dict[str, Any]:
        
        node = self.get_node(node_id)
        return node.outputs if node else {}
    
    def update_node_outputs(self, node_id: str, outputs: Dict[str, Any]) -> None:
        
        node = self.get_node(node_id)
        if node:
            node.outputs = outputs

class GraphParser:
    
    
    @staticmethod
    def parse_json(json_str: str) -> Graph:
        
        workflow_def = json.loads(json_str)
        return GraphParser._parse_workflow_def(workflow_def)
    
    @staticmethod
    def parse_yaml(yaml_str: str) -> Graph:
        
        workflow_def = yaml.safe_load(yaml_str)
        return GraphParser._parse_workflow_def(workflow_def)
    
    @staticmethod
    def parse_file(file_path: str) -> Graph:
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        
        if file_path.endswith('.json'):
            return GraphParser.parse_json(content)
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return GraphParser.parse_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path}. Please use JSON or YAML.")
    
    @staticmethod
    def _parse_workflow_def(workflow_def: Dict[str, Any]) -> Graph:
        
        graph = Graph()
        
        
        if 'nodes' in workflow_def:
            nodes_data = workflow_def['nodes']
            
            
            if isinstance(nodes_data, dict):
                
                for node_id, node_data in nodes_data.items():
                    node = Node(
                        id=node_id,
                        type=node_data['type'],
                        inputs=node_data.get('inputs', {}),
                        position=node_data.get('position'),
                        metadata=node_data.get('metadata')
                    )
                    graph.add_node(node)
            elif isinstance(nodes_data, list):
                
                for node_data in nodes_data:
                    node = Node(
                        id=node_data['id'],
                        type=node_data['type'],
                        inputs=node_data.get('inputs', {}),
                        position=node_data.get('position'),
                        metadata=node_data.get('metadata')
                    )
                    graph.add_node(node)
        
        
        if 'edges' in workflow_def:
            edges_data = workflow_def['edges']
            
            
            if isinstance(edges_data, dict):
                
                for edge_id, edge_data in edges_data.items():
                    
                    if 'source_output' in edge_data:
                        source_output = edge_data['source_output']
                    elif 'sourceOutput' in edge_data:
                        source_output = edge_data['sourceOutput']
                    else:
                        raise ValueError(f"Edge {edge_id} missing source_output or sourceOutput field")
                    
                    if 'target_input' in edge_data:
                        target_input = edge_data['target_input']
                    elif 'targetInput' in edge_data:
                        target_input = edge_data['targetInput']
                    else:
                        raise ValueError(f"Edge {edge_id} missing target_input or targetInput field")
                    
                    edge = Edge(
                        id=edge_id,
                        source=edge_data['source'],
                        source_output=source_output,
                        target=edge_data['target'],
                        target_input=target_input
                    )
                    graph.add_edge(edge)
            elif isinstance(edges_data, list):
                
                for edge_data in edges_data:
                    edge = Edge(
                        id=edge_data['id'],
                        source=edge_data['source'],
                        source_output=edge_data['source_output'],
                        target=edge_data['target'],
                        target_input=edge_data['target_input']
                    )
                    graph.add_edge(edge)
        
        return graph

def parse_graph(workflow_def: Dict[str, Any]) -> Graph:
    
    return GraphParser._parse_workflow_def(workflow_def)

def parse_graph_json(json_str: str) -> Graph:
    
    return GraphParser.parse_json(json_str)

def parse_graph_yaml(yaml_str: str) -> Graph:
    
    return GraphParser.parse_yaml(yaml_str)

def parse_graph_file(file_path: str) -> Graph:
    
    return GraphParser.parse_file(file_path)
