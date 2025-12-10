import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../types';
import { getHandleColorByDataType } from '../../utils/handleColorUtils';

interface ImageOutputNodeProps extends NodeProps {
  data: WorkflowNode['data'];
}

const ImageOutputNode: React.FC<ImageOutputNodeProps> = ({ data, selected }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  // 计算最大连接点数量，用于CSS变量设置
  const inputCount = data.inputs?.length || 0;
  const outputCount = data.outputs?.length || 0;
  const maxHandleCount = Math.max(inputCount, outputCount);

  return (
    <div 
      className={`react-flow__node generic-node ${selected ? 'selected' : ''}`} 
      onClick={handleNodeClick}
      style={{ '--handle-count': maxHandleCount } as React.CSSProperties}
    >
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* 连接区域 */}
      <div className="connection-area">
        {/* 左侧输入连接点 */}
        {data.inputs?.length > 0 && (
          <div className="handles-column left-handles">
            {data.inputs.map((input: NodeInput, index: number) => {
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
        )}

        {/* 右侧输出连接点 */}
        {data.outputs?.length > 0 && (
          <div className="handles-column right-handles">
            {data.outputs.map((output: NodeOutput, index: number) => {
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
        )}
      </div>
      
      {/* Node Content */}
      <div className="node-content">
        <div className="central-content-placeholder">
          {/* Placeholder for future content */}
        </div>
        
        {/* 参数控制区域 */}
        <div className="parameter-control-area">
        <div className="node-description">Image Output</div>
        
        <div className="image-preview-container">
          {data.imageUrl ? (
            <img
              src={data.imageUrl}
              alt="Output preview"
              className="image-preview"
            />
          ) : (
            <div className="image-placeholder">
              <span>Image Output</span>
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
          <button className="output-btn">
            Save Image
          </button>
          <button className="output-btn">
            Copy
          </button>
        </div>
      </div>
    </div>
  </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: ImageOutputNodeProps, nextProps: ImageOutputNodeProps) => {
  // 检查节点是否被选中
  if (prevProps.selected !== nextProps.selected) return false;
  
  // 检查图像数据是否变化
  if (prevProps.data.imageUrl !== nextProps.data.imageUrl) return false;
  
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

export default React.memo(ImageOutputNode as React.FC<ImageOutputNodeProps>, areEqual);
