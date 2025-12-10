import React from 'react';
import { WorkflowData } from '../types';

// Frontend types
export interface FrontendWorkflow {
  id?: string;
  name?: string;
  description?: string;
  nodes?: FrontendNode[];
  edges?: FrontendEdge[];
  createdAt?: string;
  updatedAt?: string;
}

export interface FrontendNode {
  id: string;
  type: 'InputNode' | 'OutputNode' | 'ProcessingNode' | string;
  position: { x: number; y: number };
  data: {
    label?: string;
    config?: {
      defaultValue?: any;
      operation?: string;
      outputName?: string;
    };
    params?: Record<string, any>;
    connections?: Record<string, any>;
    status?: string;
    executionTime?: number | null;
    output?: any;
  };
  status?: string;
  executionTime?: number | null;
  output?: any;
}

export interface FrontendEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  data?: { label?: string; dataType?: string };
  style?: React.CSSProperties;
}

// Backend types
export interface BackendWorkflow {
  id: string | null;
  name: string;
  description: string;
  nodes: BackendNode[];
  edges: BackendEdge[];
  created_at: string;
  updated_at: string;
}

export interface BackendNode {
  id: string;
  type: 'input' | 'output' | 'processing' | string;
  inputs: Record<string, any>;
  data: {
    label?: string;
    [key: string]: any;
  };
  position: { x: number; y: number };
  status: string;
  execution_time: number | null;
  output: any | null;
}

export interface BackendEdge {
  id: string;
  source: string;
  target: string;
  source_output: string;
  target_input: string;
  source_handle: string | undefined;
  target_handle: string | undefined;
  label: string | null;
  data_type?: string; // 添加数据类型字段
}

// Validation result type
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export const frontendToBackendWorkflow = (workflow: FrontendWorkflow | null): BackendWorkflow | null => {
  if (!workflow) return null
  
  return {
    id: workflow.id || null,
    name: workflow.name || 'Untitled Workflow',
    description: workflow.description || '',
    nodes: workflow.nodes ? workflow.nodes.map(frontendToBackendNode).filter(Boolean) as BackendNode[] : [],
    edges: workflow.edges ? workflow.edges.map(frontendToBackendEdge).filter(Boolean) as BackendEdge[] : [],
    created_at: workflow.createdAt || new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
}

export const frontendToBackendNode = (node: FrontendNode | null): BackendNode | null => {
  if (!node) return null
  
  
  const typeMap: Record<string, string> = {
    'InputNode': 'input',
    'OutputNode': 'output',
    'ProcessingNode': 'processing'
  };
  
  
  const backendType = typeMap[node.type] || node.type;
  
  
  const inputs: Record<string, any> = {};
  
  
  if (node.data.config && node.data.config.defaultValue !== undefined) {
    inputs.value = node.data.config.defaultValue;
  }
  
  
  if (node.data.config && node.data.config.operation !== undefined) {
    inputs.operation = node.data.config.operation;
  }
  
  
  if (node.data.config && node.data.config.outputName !== undefined) {
    inputs.outputName = node.data.config.outputName;
  }
  
  return {
    id: node.id,
    type: backendType,
    inputs: inputs,
    data: {
      label: node.data.label || node.type,
      ...(node.data.params || {}),
      ...(node.data.connections || {})
    },
    position: {
      x: node.position.x,
      y: node.position.y
    },
    status: node.status || 'idle',
    execution_time: node.executionTime || null,
    output: node.output || null
  }
}

export const frontendToBackendEdge = (edge: FrontendEdge | null): BackendEdge | null => {
  if (!edge) return null
  
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    source_output: edge.sourceHandle || 'output',
    target_input: edge.targetHandle || 'input',
    source_handle: edge.sourceHandle,
    target_handle: edge.targetHandle,
    label: edge.data?.label || null,
    data_type: edge.data?.dataType // 传递数据类型信息
  }
}

export const backendToFrontendWorkflow = (workflow: BackendWorkflow | null): FrontendWorkflow | null => {
  if (!workflow) return null
  
  return {
    id: workflow.id as string,
    name: workflow.name,
    description: workflow.description,
    nodes: workflow.nodes ? workflow.nodes.map(backendToFrontendNode).filter(Boolean) as FrontendNode[] : [],
    edges: workflow.edges ? workflow.edges.map(backendToFrontendEdge).filter(Boolean) as FrontendEdge[] : [],
    createdAt: workflow.created_at,
    updatedAt: workflow.updated_at
  }
}

export const backendToFrontendNode = (node: BackendNode | null): FrontendNode | null => {
  if (!node) return null
  
  
  const label = node.data.label || node.type
  
  
  const params = { ...node.data };
  delete params.label;
  delete params.connections;
  
  return {
    id: node.id,
    type: node.type,
    position: node.position,
    data: {
      label: label,
      params: params,
      connections: node.data.connections || {},
      status: node.status || 'idle',
      executionTime: node.execution_time || null,
      output: node.output || null
    },
    status: node.status || 'idle',
    executionTime: node.execution_time || null,
    output: node.output || null
  }
}

export const backendToFrontendEdge = (edge: BackendEdge | null): FrontendEdge | null => {
  if (!edge) return null
  
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.source_handle,
    targetHandle: edge.target_handle,
    data: {
      label: edge.label || '',
      dataType: edge.data_type || '' // 恢复数据类型信息
    },

    style: {
      strokeWidth: 2,
      stroke: edge.data_type === 'model' ? '#FF5733' : 
             edge.data_type === 'latent' ? '#33FF57' : 
             edge.data_type === 'prompt' ? '#3357FF' : '#888' // 根据数据类型设置颜色
    }
  }
}

export const syncWorkflowData = (frontendData: FrontendWorkflow | null, backendData: BackendWorkflow | null, syncDirection: 'frontend-to-backend' | 'backend-to-frontend' = 'frontend-to-backend'): BackendWorkflow | FrontendWorkflow | null => {
  if (syncDirection === 'frontend-to-backend') {
    return frontendToBackendWorkflow(frontendData)
  } else {
    return backendToFrontendWorkflow(backendData)
  }
}

export const mergeWorkflowData = (frontendData: FrontendWorkflow | null, backendData: BackendWorkflow | null): FrontendWorkflow | null => {
  if (!frontendData) return backendToFrontendWorkflow(backendData)
  if (!backendData) return frontendData
  
  
  const frontendUpdated = new Date(frontendData.updatedAt || 0)
  const backendUpdated = new Date(backendData.updated_at || 0)
  
  if (frontendUpdated > backendUpdated) {
    return frontendData
  } else {
    return backendToFrontendWorkflow(backendData)
  }
}

export const validateWorkflowData = (workflowData: FrontendWorkflow | null): ValidationResult => {
  const errors: string[] = []
  
  if (!workflowData) {
    errors.push('Workflow data is null or undefined')
    return { isValid: false, errors }
  }
  
  if (!Array.isArray(workflowData.nodes)) {
    errors.push('Nodes must be an array')
  } else {
    workflowData.nodes.forEach((node, index) => {
      const nodeErrors = validateNodeData(node)
      if (!nodeErrors.isValid) {
        errors.push(`Node at index ${index}: ${nodeErrors.errors.join(', ')}`)
      }
    })
  }
  
  if (!Array.isArray(workflowData.edges)) {
    errors.push('Edges must be an array')
  } else {
    workflowData.edges.forEach((edge, index) => {
      const edgeErrors = validateEdgeData(edge)
      if (!edgeErrors.isValid) {
        errors.push(`Edge at index ${index}: ${edgeErrors.errors.join(', ')}`)
      }
    })
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export const validateNodeData = (nodeData: FrontendNode | null): ValidationResult => {
  const errors: string[] = []
  
  if (!nodeData) {
    errors.push('Node data is null or undefined')
    return { isValid: false, errors }
  }
  
  if (!nodeData.id) {
    errors.push('Node must have an id')
  }
  
  if (!nodeData.type) {
    errors.push('Node must have a type')
  }
  
  if (!nodeData.position || typeof nodeData.position.x !== 'number' || typeof nodeData.position.y !== 'number') {
    errors.push('Node must have valid position coordinates')
  }
  
  if (!nodeData.data) {
    errors.push('Node must have data')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export const validateEdgeData = (edgeData: FrontendEdge | null): ValidationResult => {
  const errors: string[] = []
  
  if (!edgeData) {
    errors.push('Edge data is null or undefined')
    return { isValid: false, errors }
  }
  
  if (!edgeData.id) {
    errors.push('Edge must have an id')
  }
  
  if (!edgeData.source) {
    errors.push('Edge must have a source node id')
  }
  
  if (!edgeData.target) {
    errors.push('Edge must have a target node id')
  }
  
  if (!edgeData.sourceHandle) {
    errors.push('Edge must have a source handle')
  }
  
  if (!edgeData.targetHandle) {
    errors.push('Edge must have a target handle')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export const generateUniqueId = (prefix: string = 'id'): string => {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
}

export const extractNodeParams = (node: FrontendNode | null): Record<string, any> => {
  if (!node || !node.data) return {}
  
  const params = { ...node.data }
  delete params.label
  delete params.connections
  delete params.status
  delete params.executionTime
  delete params.output
  
  return params
}

// Convert FrontendWorkflow to WorkflowData for internal use
export const frontendWorkflowToWorkflowData = (frontendWorkflow: FrontendWorkflow): WorkflowData => {
  return {
    nodes: (frontendWorkflow.nodes || []).map(node => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: {
        label: node.data.label || node.type,
        inputs: [], // FrontendNode doesn't have inputs field, add empty array
        outputs: [], // FrontendNode doesn't have outputs field, add empty array
        params: node.data.params || {},
        ...(node.data.config ? { config: node.data.config } : {})
      }
    })),
    edges: (frontendWorkflow.edges || []).map(edge => {
      // 获取数据类型
      const dataType = edge.data?.dataType || 'default';
      
      // 根据数据类型设置颜色
      let strokeColor = '#888'; // 默认颜色
      if (dataType === 'model') {
        strokeColor = '#FF5733'; // 模型数据类型 - 橙色
      } else if (dataType === 'latent') {
        strokeColor = '#33FF57'; // 潜在数据类型 - 绿色
      } else if (dataType === 'prompt') {
        strokeColor = '#3357FF'; // 提示数据类型 - 蓝色
      }
      
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle || 'output', // Provide default value
        targetHandle: edge.targetHandle || 'input', // Provide default value
        data: {
          label: edge.data?.label || '',
          dataType: dataType
        },
        type: 'step', // 使用步进边缘
        style: {
          strokeWidth: 2,
          stroke: strokeColor
        }
      };
    })
  }
}

// Convert WorkflowData to FrontendWorkflow for validation and export
export const workflowDataToFrontendWorkflow = (workflowData: WorkflowData): FrontendWorkflow => {
  return {
    nodes: workflowData.nodes.map(node => ({
      id: node.id,
      type: node.type || 'ProcessingNode', // Provide default value for type
      position: node.position,
      data: {
        label: node.data?.label || node.type,
        params: node.data?.params || {},
        config: node.data?.config
      }
    })),
    edges: workflowData.edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      sourceHandle: edge.sourceHandle || undefined, // Convert null to undefined
      targetHandle: edge.targetHandle || undefined // Convert null to undefined
    }))
  }
}