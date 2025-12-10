import React from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeOutput, NodeParam } from '../../types';
import { getHandleColorByDataType } from '../../utils/handleColorUtils';

interface InputNodeProps {
  data: WorkflowNode['data'];
  selected?: boolean;
}

const InputNode: React.FC<InputNodeProps> = ({ data }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
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
      <div className="connection-area">
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
      
      {/* Node Content */}
      <div className="node-content">
        <div className="central-content-placeholder">
          {/* Placeholder for future content */}
        </div>
        
        {/* 参数控制区域 */}
        <div className="parameter-control-area">
        {Object.entries(data.params || {}).map(([key, param]) => {
          const typedParam = param as NodeParam;
          return (
            <div key={key} className="param-group">
              <label className="param-label">{typedParam.label}</label>
              <input
                type={typedParam.type}
                value={typedParam.value}
                className="node-input"
                onChange={(e) => {
                  // This would typically be handled by a parent component's state management
                  console.log('Input changed:', key, e.target.value);
                }}
              />
            </div>
          );
        })}
        </div>
      </div>
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: InputNodeProps, nextProps: InputNodeProps) => {
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

export default React.memo(InputNode as React.FC<InputNodeProps>, areEqual);
