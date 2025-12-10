import React, { useState, useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface LoadVaeNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

interface ModelInfo {
  path: string;
  name: string;
  type: string;
  size: number;
}

const LoadVaeNode: React.FC<LoadVaeNodeProps> = ({ data, onDataChange }) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // 从后端获取VAE模型列表
  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/models?model_type=vae');
      const result = await response.json();
      setModels(result.models || []);
    } catch (error) {
      console.error('Failed to fetch VAE models:', error);
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
    console.log('Selected VAE model path:', selectedModelPath);

    // 更新节点数据
    if (onDataChange && data.params) {
      const updatedParams = {
        ...data.params,
        vaePath: {
          ...data.params.vaePath,
          value: selectedModelPath
        }
      };
      onDataChange(data.id || '', {
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
    if (onDataChange && data.params) {
      const updatedParams = {
        ...data.params,
        [key]: {
          ...data.params[key],
          value
        }
      };
      onDataChange(data.id || '', {
        ...data,
        params: updatedParams
      });
    }
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node load-vae-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
      <div className="connection-area">
        {/* Input handles */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput) => (
            <div key={input.name} className="handle-item">
              <Handle
                type="target"
                position={Position.Left}
                id={`${input.name}-handle`}
                className="node-handle"
                style={{
                  left: 0,
                  background: getHandleColorByDataType(input.type || '')
                }}
              />
              <span className="handle-label">{input.name}</span>
            </div>
          ))}
        </div>
        
        {/* Node content */}
        <div className="node-content-wrapper">
          <div className="node-header">
            <span>{data.label}</span>
          </div>
          <div className="node-content">
            <div className="param-group">
              <label className="param-label">VAE Model</label>
              {isLoading ? (
                <div className="model-loading">Loading VAE models...</div>
              ) : (
                <select
                  value={data.params?.vaePath?.value || ''}
                  className="node-select"
                  onChange={handleModelChange}
                  style={{ width: '100%', padding: '8px', marginTop: '4px' }}
                >
                  <option value="">Select a VAE model...</option>
                  {models.map((model, index) => (
                    <option key={index} value={model.path}>
                      {model.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
            
            {Object.entries(data.params || {}).map(([key, param]) => {
              if (key !== 'vaePath') {
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
        
        {/* Output handles */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput) => (
            <div key={output.name} className="handle-item">
              <Handle
                type="source"
                position={Position.Right}
                id={`${output.name}-handle`}
                className="node-handle"
                style={{
                  right: 0,
                  background: getHandleColorByDataType(output.type || '')
                }}
              />
              <span className="handle-label">{output.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LoadVaeNode;