import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';

interface ClipTextEncodeNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const ClipTextEncodeNode: React.FC<ClipTextEncodeNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  // 处理参数变化
  const handleParamChange = (paramName: string, value: any) => {
    console.log('Text changed:', value);
    if (onDataChange && data.params) {
      const updatedParams = { ...data.params };
      if (updatedParams[paramName]) {
        updatedParams[paramName].value = value;
      } else {
        // 如果参数不存在，则创建它
        updatedParams[paramName] = { value, type: typeof value };
      }
      
      onDataChange(nodeId || '', { ...data, params: updatedParams });
    }
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className={`cognot-node-base clip-text-encode-node`} onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* 连接区域 */}
      <div className="connection-area">
        {/* Input handles with labels */}
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
                  style={{ left: 0 }}
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
            const handleKey = output.id || output.name || `output-${index}`;
            const handleId = output.id || output.name || `output-${index}`;
            
            return (
              <div key={handleKey} className="handle-item">
                <Handle
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
      
      {/* 节点内容区域 */}
      <div className="node-content-area">
        <div className="node-content">
          <div className="text-input-container">
            <textarea
              value={data.params?.text?.value || ''}
              placeholder="Enter text prompt"
              className="node-input node-textarea"
              rows={3}
              onChange={(e) => {
                handleParamChange('text', e.target.value);
              }}
            />
          </div>
          
          {/* Additional parameters */}
          {Object.entries(data.params || {}).map(([key, param]) => {
            if (key !== 'text') {
              const typedParam = param as NodeParam;
              return (
                <div key={key} className="param-group">
                  <label className="param-label">{typedParam.label}</label>
                  <input
                    type={typedParam.type === 'number' ? 'number' : 'text'}
                    value={typedParam.value}
                    className="node-input"
                    onChange={(e) => {
                      handleParamChange(key, e.target.value);
                    }}
                  />
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>
    </div>
  );
};

export default ClipTextEncodeNode;