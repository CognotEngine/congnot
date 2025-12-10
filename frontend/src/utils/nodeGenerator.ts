import { NodeData, NodeInput, NodeOutput, NodeParam, BaseNodeData } from '../types';
import { SingleNodeMetadata } from '../types';

// 从后端节点元数据生成前端通用节点的数据结构
export const generateNodeDataFromMetadata = (metadata: SingleNodeMetadata, nodeType: string): NodeData => {
  // 提取输入参数
  const inputs: NodeInput[] = Object.entries(metadata.input_schema.properties).map(([name, prop]) => ({
    name,
    label: prop.title || name,
    type: prop.type
  }));

  // 提取输出参数
  const outputs: NodeOutput[] = Object.entries(metadata.output_schema.properties).map(([name, prop]) => ({
    name,
    label: prop.title || name,
    type: prop.type
  }));

  // 提取参数配置
  const params: Record<string, NodeParam> = {};
  Object.entries(metadata.input_schema.properties).forEach(([name, prop]) => {
    // 跳过输入连接点参数
    if (prop.type === 'object' && prop.format === 'node-handle') {
      return;
    }

    params[name] = {
      name,
      label: prop.title || name,
      type: prop.type,
      value: prop.default || '',
      description: prop.description || '',
      required: metadata.input_schema.required.includes(name),
      widget_meta: {
        widget_type: determineWidgetType(prop),
        label: prop.title || null,
        min_value: prop.minimum,
        max_value: prop.maximum,
        step: prop.multipleOf,
        options: prop.enum,
        color_type: null,
        display_mode: 'default'
      }
    };
  });

  return {
    label: metadata.name || nodeType,
    type: nodeType as BaseNodeData['type'],
    inputs,
    outputs,
    params
  } as NodeData;
};

// 根据后端属性类型确定前端控件类型
const determineWidgetType = (prop: any): string => {
  if (prop.enum) {
    return 'combo';
  } else if (prop.type === 'number') {
    return 'slider';
  } else if (prop.type === 'boolean') {
    return 'toggle';
  } else if (prop.type === 'string') {
    return 'text';
  } else {
    return 'text';
  }
};

// 更新NodePalette中的节点定义，确保与后端一致
export const updateNodePaletteFromMetadata = (paletteNodes: any[], nodeMetadata: Record<string, SingleNodeMetadata>) => {
  return paletteNodes.map(node => {
    if (nodeMetadata[node.type]) {
      const metadata = nodeMetadata[node.type];
      return {
        ...node,
        inputs: generateInputsFromMetadata(metadata),
        outputs: generateOutputsFromMetadata(metadata)
      };
    }
    return node;
  });
};

// 从后端元数据生成输入连接点
const generateInputsFromMetadata = (metadata: SingleNodeMetadata): NodeInput[] => {
  // 对于stable_diffusion_generate节点，保留所有输入
  if (metadata.name === 'stable_diffusion_generate') {
    return Object.entries(metadata.input_schema.properties)
      .map(([name, prop]) => ({
        name,
        label: prop.title || name,
        type: prop.properties?.data_type?.enum?.[0] || prop.type || 'default'
      }));
  }
  
  return Object.entries(metadata.input_schema.properties)
    .filter(([_, prop]) => prop.type === 'object' && prop.format === 'node-handle')
    .map(([name, prop]) => ({
      name,
      label: prop.title || name,
      type: prop.properties?.data_type?.enum?.[0] || 'default'
    }));
};

// 从后端元数据生成输出连接点
const generateOutputsFromMetadata = (metadata: SingleNodeMetadata): NodeOutput[] => {
  // 对于stable_diffusion_generate节点，保留所有输出
  if (metadata.name === 'stable_diffusion_generate') {
    return Object.entries(metadata.output_schema.properties)
      .map(([name, prop]) => ({
        name,
        label: prop.title || name,
        type: prop.properties?.data_type?.enum?.[0] || prop.type || 'default'
      }));
  }
  
  return Object.entries(metadata.output_schema.properties)
    .filter(([_, prop]) => prop.type === 'object' && prop.format === 'node-handle')
    .map(([name, prop]) => ({
      name,
      label: prop.title || name,
      type: prop.properties?.data_type?.enum?.[0] || 'default'
    }));
};
