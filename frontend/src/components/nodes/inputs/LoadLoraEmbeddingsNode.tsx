import React, { useState, useEffect } from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';

interface LoadLoraEmbeddingsNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

interface ModelInfo {
  path: string;
  name: string;
  type: string;
  size: number;
}

const LoadLoraEmbeddingsNode: React.FC<LoadLoraEmbeddingsNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  const [loraModels, setLoraModels] = useState<ModelInfo[]>([]);
  const [embeddings, setEmbeddings] = useState<ModelInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('lora'); // 'lora' or 'embedding'

  // 从后端获取LoRA和embeddings模型列表
  const fetchModels = async () => {
    setIsLoading(true);
    try {
      // 获取LoRA模型
      const loraResponse = await fetch('/models?model_type=loras');
      const loraResult = await loraResponse.json();
      setLoraModels(loraResult.models || []);

      // 获取embeddings
      const embeddingResponse = await fetch('/models?model_type=embeddings');
      const embeddingResult = await embeddingResponse.json();
      setEmbeddings(embeddingResult.models || []);
    } catch (error) {
      console.error('Failed to fetch LoRA/embedding models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 组件加载时获取模型列表
  useEffect(() => {
    fetchModels();
  }, []);

  // 处理模型类型选择变化
  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedType(e.target.value);
    // 清空文件路径当类型改变时
    if (onDataChange && data.params) {
      const updatedParams = {
        ...data.params,
        filePath: {
          ...data.params.filePath,
          value: ''
        }
      };
      onDataChange(nodeId || '', {
        ...data,
        params: updatedParams
      });
    }
  };

  // 处理模型选择变化
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedModelPath = e.target.value;
    console.log(`Selected ${selectedType} path:`, selectedModelPath);

    // 更新节点数据
    if (onDataChange && data.params) {
      const updatedParams = {
        ...data.params,
        filePath: {
          ...data.params.filePath,
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
    if (key === 'strength' || key === 'weight' || key === 'scale') {
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

  // 获取当前类型的模型列表
  const currentModels = selectedType === 'lora' ? loraModels : embeddings;

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node load-lora-embeddings-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
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
          <label className="param-label">Model Type</label>
          <select
            value={selectedType}
            className="node-select"
            onChange={handleTypeChange}
            style={{ width: '100%', padding: '8px', marginTop: '4px', marginBottom: '8px' }}
          >
            <option value="lora">LoRA</option>
            <option value="embedding">Embedding</option>
          </select>
        </div>
        
        <div className="param-group">
          <label className="param-label">{selectedType === 'lora' ? 'LoRA' : 'Embedding'} File</label>
          {isLoading ? (
            <div className="model-loading">Loading {selectedType} files...</div>
          ) : (
            <select
              value={data.params?.filePath?.value || ''}
              className="node-select"
              onChange={handleModelChange}
              style={{ width: '100%', padding: '8px', marginTop: '4px' }}
            >
              <option value="">Select a {selectedType} file...</option>
              {currentModels.map((model, index) => (
                <option key={index} value={model.path}>
                  {model.name}
                </option>
              ))}
            </select>
          )}
        </div>
        
        <div className="param-group">
          <label className="param-label">Strength</label>
          <input
            type="number"
            value={data.params?.strength?.value || 1.0}
            min="0"
            max="1"
            step="0.1"
            className="node-input"
            onChange={(e) => handleParamChange('strength', e.target.value)}
          />
        </div>
        
        {Object.entries(data.params || {}).map(([key, param]) => {
          if (key !== 'filePath' && key !== 'strength') {
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

export default LoadLoraEmbeddingsNode;