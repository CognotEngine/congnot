import { Node, Edge } from 'reactflow';

// Define WorkflowNode and WorkflowEdge types as aliases for React Flow's Node and Edge
export type WorkflowNode = Node;
export type WorkflowEdge = Edge;

// 节点类型定义
export interface Condition {
  type: 'AND' | 'OR';
  conditions?: Condition[];
  param?: string;
  operator?: string;
  value?: any;
}

export interface NodeParam {
  name: string;
  label: string;
  type: string;
  value?: any;
  options?: any[];
  description?: string;
  properties?: any;
  items?: any[];
  step?: number;
  required?: boolean;
  widget_meta?: {
    widget_type: string;
    label?: string | null;
    min_value?: number;
    max_value?: number;
    step?: number;
    options?: any[] | null;
    color_type?: string | null;
    display_mode?: string;
  };
  metadata?: {
    widget_meta?: {
      widget_type: string;
      label?: string | null;
      min_value?: number;
      max_value?: number;
      step?: number;
      options?: any[] | null;
      color_type?: string | null;
      display_mode?: string;
    };
    render_as?: string;
  };
  condition?: Condition;
}

export interface NodeInput {
  name?: string;
  id?: string;
  label: string;
  type?: string;
}

export interface NodeOutput {
  name?: string;
  id?: string;
  label: string;
  type?: string;
}

// 基础节点数据结构
export interface BaseNodeData {
  label: string;
  type: string;
  inputs: NodeInput[];
  outputs: NodeOutput[];
  params: Record<string, NodeParam>;
  description?: string;
  category?: string;
  icon?: string;
}

// 特定节点类型的数据扩展
export interface TextNodeData extends BaseNodeData {
  type: 'TextInput' | 'TextOutput' | 'FileInput' | 'APIInput' | 'DatabaseInput' | 'TextProcessing';
  content?: string;
}

export interface AIGeneratorNodeData extends BaseNodeData {
  type: 'stable_diffusion_generate' | 'stable_diffusion_image_to_image' | 'stable_diffusion_controlnet';
  executionStatus?: string;
  preview?: string;
}

export interface ImageNodeData extends BaseNodeData {
  type: 'imageInput' | 'imageOutput' | 'saveImage' | 'imageManipulation' | 'previewNode';
  imageUri?: string;
  preview?: string;
}

export interface VideoNodeData extends BaseNodeData {
  type: 'videoLoad' | 'frameIndexManager' | 'opticalFlowCalculator' | 'frameProcessorLoop' | 'fusionImage' | 'videoComposer';
  videoUri?: string;
  frameCount?: number;
}

export interface ThirdPartyAINodeData extends BaseNodeData {
  type: 'KSampler' | 'ClipTextEncode' | 'CheckpointLoaderSimple';
  model?: string;
}

export interface MathNodeData extends BaseNodeData {
  type: 'MathOperation' | 'AddNumbers' | 'MultiplyNumbers' | 'ConcatenateStrings';
  result?: number | string;
}

export interface ControlFlowNodeData extends BaseNodeData {
  type: 'Loop' | 'processing' | 'filter' | 'reroute' | 'constant';
  loopCount?: number;
}

// 所有节点数据的联合类型
export type CognotNodeData = TextNodeData | AIGeneratorNodeData | ImageNodeData | VideoNodeData | ThirdPartyAINodeData | MathNodeData | ControlFlowNodeData;

// 保持向后兼容性
export type NodeData = CognotNodeData & {
  param_status?: Record<string, any>;
  is_class?: boolean;
  rightLabel?: string;
}

// React Flow compatible types
export interface NodePosition {
  x: number;
  y: number;
}

export interface Viewport {
  x: number;
  y: number;
  zoom: number;
}

// 工作流数据类型定义 - Using React Flow's Node and Edge types
export interface WorkflowData {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

// 执行状态类型定义
export interface ExecutionStatus {
  isExecuting: boolean;
  progress: number;
  status: string;
  id?: string;
  results?: any;
}

// 单个节点元数据类型定义
export interface SingleNodeMetadata {
  name?: string;
  class_name?: string;
  input_schema: {
    properties: Record<string, any>;
    required: string[];
  };
  output_schema: {
    properties: Record<string, any>;
    required: string[];
  };
  description?: string;
  category?: string;
  icon?: string;
  is_class?: boolean;
}

// 节点元数据缓存类型定义
export interface NodeMetadata {
  [nodeType: string]: SingleNodeMetadata;
}

// 连接中边类型定义
export interface ConnectingEdge {
  source: string;
  sourceHandle: string;
  targetX: number;
  targetY: number;
}

// 悬停句柄类型定义
export interface HoveredHandle {
  nodeId: string;
  handleId: string;
  handleType: 'source' | 'target';
}

// 节点配置类型定义
export interface NodePort {
  id: string;
  type: string;
  label: string;
  name?: string;
}

export interface NodeConfig {
  type?: string;
  operation?: string;
  defaultValue?: string;
  outputName?: string;
}

// 调色板节点类型定义
export interface PaletteNode {
  id: string;
  type: string;
  label: string;
  description: string;
  category?: string;
  config?: NodeConfig;
  inputs?: NodePort[];
  outputs?: NodePort[];
  icon?: React.ReactNode;
  workflowData?: SavedWorkflow;
}

// 分类类型定义
export interface Category {
  id: string;
  name: string;
  icon: React.ReactNode;
  nodes: PaletteNode[];
}

// 保存的工作流类型定义
export interface SavedWorkflow {
  id: string;
  name: string;
  data: {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
  };
  createdAt: string;
}

// 不再需要的上下文相关类型已移除，因为我们现在使用React Flow的内置状态管理
