import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface SaveImageNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
  selected?: boolean;
}

const SaveImageNode: React.FC<SaveImageNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  
  // 处理参数变化
  const handleParamChange = (paramName: string, value: any) => {
    if (onDataChange && data.params) {
      const updatedParams = { ...data.params };
      if (updatedParams[paramName]) {
        updatedParams[paramName].value = value;
      }
      
      onDataChange(nodeId || '', { ...data, params: updatedParams });
    }
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node generic-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
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
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        <div className="image-preview-container">
          {data.imageUrl ? (
            <img
              src={data.imageUrl}
              alt="Image to save"
              className="preview-image"
            />
          ) : (
            <div className="no-image-placeholder">
              <span>Image Preview</span>
            </div>
          )}
        </div>
        
              {Object.entries(data.params || {}).map(([key, param]) => {
          const typedParam = param as NodeParam;
          if (typedParam.type === 'select') {
            return (
              <div key={key} className="param-group">
                <label className="param-label">{typedParam.label}</label>
                <select
                  value={typedParam.value}
                  className="node-input"
                  onChange={(e) => {
                    handleParamChange(key, e.target.value);
                  }}
                >
                  {typedParam.options?.map((option) => (
                    <option key={option.value} value={option.value}>{option.label || option.value}</option>
                  ))}
                </select>
              </div>
            );
          } else {
            return (
              <div key={key} className="param-group">
                <label className="param-label">{typedParam.label}</label>
                <input
                  type={typedParam.type === 'number' ? 'number' : 'text'}
                  value={typedParam.value}
                  className="node-input"
                  onChange={(e) => {
                    const newValue = typedParam.type === 'number' 
                      ? parseFloat(e.target.value) || 0 
                      : e.target.value;
                    handleParamChange(key, newValue);
                  }}
                />
              </div>
            );
          }
        })}
        
        <div className="output-controls">
          <button
            className="save-image-button"
            onClick={() => {
              console.log('Save image clicked');
              // 实际保存图像的逻辑将由父组件处理
            }}
          >
            Save Image
          </button>
        </div>
      </div>
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: SaveImageNodeProps, nextProps: SaveImageNodeProps) => {
  // 检查节点是否被选中
  if (prevProps.selected !== nextProps.selected) return false;
  
  // 检查参数值是否变化
  const prevParams = prevProps.data.params || {};
  const nextParams = nextProps.data.params || {};
  const paramKeys = [...new Set([...Object.keys(prevParams), ...Object.keys(nextParams)])];
  
  for (const key of paramKeys) {
    const prevParam = prevParams[key];
    const nextParam = nextParams[key];
    
    // 检查参数是否存在或值是否变化
    if (!prevParam || !nextParam) return false;
    if (prevParam.value !== nextParam.value) return false;
  }
  
  // 所有关键属性都没有变化，不需要重渲染
  return true;
};

export default React.memo(SaveImageNode as React.FC<SaveImageNodeProps>, areEqual);