import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface VAEDecodeNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const VAEDecodeNode: React.FC<VAEDecodeNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  
  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);
  
  // 处理参数变化
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
  return (
    <div className="react-flow__node generic-node" onClick={handleNodeClick} id={`node-${nodeId}`}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* 连接区域 */}
      <div className="connection-area" style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
        {/* Input handles - Concentrated layout */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput, index: number) => {
            // 使用id或name作为key，如果都不存在则使用索引
            const handleKey = input.id || input.name || `input-${index}`;
            // 使用id或name作为handle的id，如果都不存在则使用索引
            const handleId = input.id || input.name || `input-${index}`;
            
            return (
              <div key={handleKey} className="handle-item">
                <Handle
                  type="target"
                  position={Position.Left}
                  id={`${handleId}-handle`}
                  className="node-handle"
                  style={{
                    background: getHandleColorByDataType(input.type || ''),
                    left: 0
                  }}
                />
                <span className="handle-label">{input.name}</span>
              </div>
            );
          })}
        </div>
        
        {/* Output handles - Concentrated layout */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput, index: number) => {
            // 使用id或name作为key，如果都不存在则使用索引
            const handleKey = output.id || output.name || `output-${index}`;
            // 使用id或name作为handle的id，如果都不存在则使用索引
            const handleId = output.id || output.name || `output-${index}`;
            
            return (
              <div key={handleKey} className="handle-item">
                <Handle
                  type="source"
                  position={Position.Right}
                  id={`${handleId}-handle`}
                  className="node-handle"
                  style={{
                    background: getHandleColorByDataType(output.type || ''),
                    right: 0
                  }}
                />
                <span className="handle-label">{output.name}</span>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Node Content */}
      <div className="node-content">
        <div className="central-content-placeholder">
          {/* Placeholder for future content */}
        </div>
        
        {/* 参数控制区域 */}
        <div className="parameter-control-area">
          <div className="node-description">
            Decodes latent representations into images using a VAE (Variational Autoencoder).
          </div>
          
          <div className="param-group">
            <label className="param-label">Latent Scale</label>
            <input
              type="number"
              value={data.params?.latentScale?.value || 1.0}
              min="0.1"
              max="5.0"
              step="0.1"
              className="node-input"
              onChange={(e) => {
                handleParamChange('latentScale', parseFloat(e.target.value) || 1.0);
              }}
            />
          </div>
          
          <div className="param-group">
            <label className="param-label">Decode Batch Size</label>
            <input
              type="number"
              value={data.params?.decodeBatchSize?.value || 1}
              min="1"
              max="16"
              step="1"
              className="node-input"
              onChange={(e) => {
                handleParamChange('decodeBatchSize', parseInt(e.target.value) || 1);
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default VAEDecodeNode;