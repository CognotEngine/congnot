import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../types';

interface PromptNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
  selected?: boolean;
}

const PromptNode: React.FC<PromptNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  
  // 处理内容变化
  const handleContentChange = (content: string) => {
    if (onDataChange) {
      onDataChange(nodeId || '', { ...data, content });
    }
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
    <div className="react-flow__node generic-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* Connection area with labeled handles */}
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
                  style={{ left: 0 }}
                />
                <span className="handle-label">{input.name}</span>
              </div>
            );
          })}
        </div>
        
        {/* Central content area */}
        <div className="central-content-placeholder"></div>
        
        {/* Right handles column */}
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
                  style={{ right: 0 }}
                />
                <span className="handle-label">{output.name}</span>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        <div className="param-group">
          <label className="param-label">Prompt</label>
          <textarea
            value={data.content || ''}
            className="node-input node-textarea"
            rows={4}
            placeholder="Enter your prompt here..."
            onChange={(e) => {
              handleContentChange(e.target.value);
            }}
          />
        </div>
        
        {Object.entries(data.params || {}).map(([key, param]) => {
          const typedParam = param as NodeParam;
          return (
            <div key={key} className="param-group">
              <label className="param-label">{typedParam.label}</label>
              <input
                type={typedParam.type === 'number' ? 'number' : 'text'}
                value={typedParam.value}
                className="node-input"
                onChange={(e) => {
                  const newValue = typedParam.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
                  handleParamChange(key, newValue);
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: PromptNodeProps, nextProps: PromptNodeProps) => {
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

export default React.memo(PromptNode as React.FC<PromptNodeProps>, areEqual);
