import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface ConstantNodeProps {
  data: WorkflowNode['data'];
  onDataChange: (nodeId: string, updatedData: Partial<WorkflowNode['data']>) => void;
}

const ConstantNode: React.FC<ConstantNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  const handleParamChange = (paramName: string, value: string | number | boolean) => {
    onDataChange(nodeId || '', {
      params: {
        ...data.params,
        [paramName]: {
          ...data.params?.[paramName],
          value
        }
      }
    });
  };

  // 数据类型选项
  const dataTypes = ['string', 'number', 'boolean'];
  
  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node constant-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      <div className="node-content">
        <div className="param-group">
          <label className="param-label">Type</label>
          <select
            value={data.params?.dataType?.value || 'string'}
            className="node-input"
            onChange={(e) => {
              handleParamChange('dataType', e.target.value);
            }}
          >
            {dataTypes.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
        
        <div className="param-group">
          <label className="param-label">Value</label>
          {data.params?.dataType?.value === 'boolean' ? (
            <select
                value={data.params?.value?.value || 'false'}
                className="node-input"
                onChange={(e) => {
                  handleParamChange('value', e.target.value === 'true');
                }}
              >
              <option value="true">True</option>
              <option value="false">False</option>
            </select>
          ) : (
            <input
              type={data.params?.dataType?.value || 'string'}
              value={data.params?.value?.value || ''}
              className="node-input"
              onChange={(e) => {
                const value = data.params?.dataType?.value === 'number' 
                  ? parseFloat(e.target.value) || 0
                  : e.target.value;
                handleParamChange('value', value);
              }}
            />
          )}
        </div>
      </div>
      
      {/* 连接区域 */}
      <div className="connection-area">
        {/* Left handles column */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput, index: number) => {
            // 使用id或name作为key，如果都不存在则使用索引
            const handleKey = input.id || input.name || `input-${index}`;
            // 使用id或name作为handle的id，如果都不存在则使用索引
            const handleId = input.id || input.name || `input-${index}`;
            
            return (
              <div key={handleKey} className="handle-item">
                <Handle
                  key={handleKey}
                  type="target"
                  position={Position.Left}
                  id={`${handleId}-handle`}
                  className="node-handle"
                  style={{
                    left: 0,
                    background: getHandleColorByDataType(input.type || '')
                  }}
                />
                <span className="handle-label">{input.name}</span>
              </div>
            );
          })}
        </div>
        
        {/* Central content placeholder */}
        <div className="central-content-placeholder"></div>
        
        {/* Output handles with labels */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput, index: number) => {
            // 使用id或name作为key，如果都不存在则使用索引
            const handleKey = output.id || output.name || `output-${index}`;
            // 使用id或name作为handle的id，如果都不存在则使用索引
            const handleId = output.id || output.name || `output-${index}`;
            
            return (
              <div key={handleKey} className="handle-item">
                <Handle
                  key={handleKey}
                  type="source"
                  position={Position.Right}
                  id={`${handleId}-handle`}
                  className="node-handle"
                  style={{
                    right: 0,
                    background: getHandleColorByDataType(output.type || '')
                  }}
                />
                <span className="handle-label">{output.name}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ConstantNode;