import React, { useState, useEffect } from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';

interface LoadCheckpointNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

interface ModelInfo {
  path: string;
  name: string;
  type: string;
  size: number;
}

const LoadCheckpointNode: React.FC<LoadCheckpointNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // 从后端获取模型列表
  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/models?model_type=checkpoints');
      const result = await response.json();
      setModels(result.models || []);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 组件加载时获取模型列表
  useEffect(() => {
    fetchModels();
  }, []);

  // 处理模型选择变化
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedModelPath = e.target.value;
    console.log('Selected model path:', selectedModelPath);

    // 更新节点数据
    if (onDataChange && data.params) {
      const updatedParams = {
        ...data.params,
        modelPath: {
          ...data.params.modelPath,
          value: selectedModelPath
        }
      };
      onDataChange(nodeId || '', {
        ...data,
        params: updatedParams
      });
    }
  };

  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  const handleParamChange = (key: string, value: any) => {
    console.log('Param changed:', key, value);
    // 对数值类型进行转换
    let processedValue = value;
    if (key === 'strength' || key === 'weight' || key === 'scale' || key === 'clip_skip') {
      processedValue = parseFloat(value) || 0;
    }
    
    if (onDataChange && data.params) {
      const updatedParams = {
        ...data.params,
        [key]: {
          ...data.params[key],
          value: processedValue
        }
      };
      onDataChange(nodeId || '', {
        ...data,
        params: updatedParams
      });
    }
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node load-checkpoint-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* Connection area with labeled handles */}
      <div className="connection-area">
        {/* Left handles column */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput) => (
            <div key={input.name} className="handle-item">
              <Handle
                key={input.name}
                type="target"
                position={Position.Left}
                id={`${input.name}-handle`}
                className="node-handle"
                style={{ left: 0 }}
              />
              <span className="handle-label">{input.name}</span>
            </div>
          ))}
        </div>
        
        {/* Central content area */}
        <div className="central-content-placeholder"></div>
        
        {/* Right handles column */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput) => (
            <div key={output.name} className="handle-item">
              <Handle
                key={output.name}
                type="source"
                position={Position.Right}
                id={`${output.name}-handle`}
                className="node-handle"
                style={{ right: 0 }}
              />
              <span className="handle-label">{output.name}</span>
            </div>
          ))}
        </div>
      </div>
      
      <div className="node-content">
        <div className="param-group">
          <label className="param-label">Model</label>
          {isLoading ? (
            <div className="model-loading">Loading models...</div>
          ) : (
            <select
              value={data.params?.modelPath?.value || ''}
              className="node-select"
              onChange={handleModelChange}
              style={{ width: '100%', padding: '8px', marginTop: '4px' }}
            >
              <option value="">Select a model...</option>
              {models.map((model, index) => (
                <option key={index} value={model.path}>
                  {model.name}
                </option>
              ))}
            </select>
          )}
        </div>
        
        {Object.entries(data.params || {}).map(([key, param]) => {
          if (key !== 'modelPath') {
            const typedParam = param as NodeParam;
            return (
              <div key={key} className="param-group">
                <label className="param-label">{typedParam.label}</label>
                <input
                  type={typedParam.type}
                  value={typedParam.value}
                  className="node-input"
                  onChange={(e) => handleParamChange(key, e.target.value)}
                />
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

export default LoadCheckpointNode;