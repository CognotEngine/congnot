import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../types';
import { getHandleColorByDataType } from '../../utils/handleColorUtils';

interface TextOutputNodeProps extends NodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const TextOutputNode: React.FC<TextOutputNodeProps> = ({ data, selected }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  return (
    <div className={`react-flow__node generic-node ${selected ? 'selected' : ''}`} onClick={handleNodeClick} style={{ '--handle-count': Math.max(data.inputs?.length || 0, data.outputs?.length || 0) } as React.CSSProperties}>
      <div className="node-header">
        <span>{data.label || 'Text Output'}</span>
      </div>
      
      {/* Connection area with labeled handles */}
      <div className="connection-area">
        {/* Left handles column */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput, index: number) => {
            const handleKey = input.id || input.name || `input-${index}`;
            const handleId = input.id || input.name || `input-${index}`;
            
            return (
              <div key={handleKey} className="handle-item">
                <Handle
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
        
        {/* Right handles column */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput, index: number) => {
            const handleKey = output.id || output.name || `output-${index}`;
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
      
      {/* Node content area */}
      <div className="node-content">
        <div className="central-content-placeholder">
          {/* Placeholder for future content */}
        </div>
        
        {/* Parameter control area */}
        <div className="parameter-control-area">
          <div className="node-description">
            {data.description || 'A node for displaying text output'}
          </div>
          
          {/* Text output area */}
          <div className="text-output-container">
            {data.output?.result ? (
              <div className="text-output">
                {data.output.result}
              </div>
            ) : (
              <div className="text-placeholder">
                <span>No text output</span>
              </div>
            )}
          </div>
          
          {/* Output details */}
          {data.outputs?.map((output: NodeOutput, index: number) => {
            const handleKey = output.id || output.name || `output-${index}`;
            
            return (
              <div key={handleKey} className="node-output">
                <label>{output.label}</label>
              </div>
            );
          })}
          
          {/* Output controls */}
          <div className="output-controls">
            <button 
              className="output-btn"
              onClick={() => {
                if (data.output?.result) {
                  navigator.clipboard.writeText(data.output.result);
                }
              }}
            >
              Copy
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: TextOutputNodeProps, nextProps: TextOutputNodeProps) => {
  // 检查节点是否被选中
  if (prevProps.selected !== nextProps.selected) return false;
  
  // 检查文本内容是否变化
  if (prevProps.data.text !== nextProps.data.text) return false;
  
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

export default React.memo(TextOutputNode as React.FC<TextOutputNodeProps>, areEqual);