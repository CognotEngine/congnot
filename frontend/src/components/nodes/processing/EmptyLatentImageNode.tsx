import React from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface EmptyLatentImageNodeProps {
  data: WorkflowNode['data'];
}

const EmptyLatentImageNode: React.FC<EmptyLatentImageNodeProps> = ({ data }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node generic-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
      <div className="connection-area">
        {/* Input handles - Concentrated layout */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput, _: number) => (
            <div key={input.name} className="handle-item">
              <Handle
                    type="target"
                    position={Position.Left}
                    id={`${input.name}-handle`}
                    className="node-handle"
                    style={{
                      background: getHandleColorByDataType(input.type || ''),
                      left: 0
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
              <label className="param-label">Width</label>
              <input
                type="number"
                value={data.params?.width?.value || 512}
                min="64"
                max="4096"
                step="64"
                className="node-input"
                onChange={(e) => {
                  console.log('Width changed:', e.target.value);
                }}
              />
            </div>
            
            <div className="param-group">
              <label className="param-label">Height</label>
              <input
                type="number"
                value={data.params?.height?.value || 512}
                min="64"
                max="4096"
                step="64"
                className="node-input"
                onChange={(e) => {
                  console.log('Height changed:', e.target.value);
                }}
              />
            </div>
            
            <div className="param-group">
              <label className="param-label">Batch Size</label>
              <input
                type="number"
                value={data.params?.batchSize?.value || 1}
                min="1"
                max="16"
                step="1"
                className="node-input"
                onChange={(e) => {
                  console.log('Batch size changed:', e.target.value);
                }}
              />
            </div>
            
            {Object.entries(data.params || {}).map(([key, param]) => {
              if (key !== 'width' && key !== 'height' && key !== 'batchSize') {
                const typedParam = param as NodeParam;
                return (
                  <div key={key} className="param-group">
                    <label className="param-label">{typedParam.label}</label>
                    <input
                      type={typedParam.type}
                      value={typedParam.value}
                      className="node-input"
                      onChange={(e) => {
                        console.log('Param changed:', key, e.target.value);
                      }}
                    />
                  </div>
                );
              }
              return null;
            })}
          </div>
        </div>
        
        {/* Output handles - Concentrated layout */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput, _: number) => (
            <div key={output.name} className="handle-item">
              <Handle
                    type="source"
                    position={Position.Right}
                    id={`${output.name}-handle`}
                    className="node-handle"
                    style={{
                      background: getHandleColorByDataType(output.type || ''),
                      right: 0
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

export default EmptyLatentImageNode;