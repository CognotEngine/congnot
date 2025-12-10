import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface ImageInputNodeProps extends NodeProps {
  data: WorkflowNode['data'];
}

const ImageInputNode: React.FC<ImageInputNodeProps> = ({ id, data, selected }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className={`react-flow__node generic-node ${selected ? 'selected' : ''}`} onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* 连接区域 */}
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
        
        {/* Central content placeholder */}
        <div className="central-content-placeholder"></div>
        
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
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        <div className="image-input-container">
          {data.imageUrl ? (
            <img
              src={data.imageUrl}
              alt="Input image"
              className="preview-image"
            />
          ) : (
            <div className="no-image-placeholder">
              <span>Upload Image</span>
            </div>
          )}
          
          <div className="image-input-controls">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = (event) => {
                    console.log('Image loaded:', event.target?.result);
                  };
                  reader.readAsDataURL(file);
                }
              }}
              style={{ display: 'none' }}
              id={`${id}-file-input`}
            />
            <label htmlFor={`${id}-file-input`} className="save-image-button">
              Choose File
            </label>
            <button
              className="save-image-button"
              onClick={() => {
                console.log('Clear image');
              }}
            >
              Clear
            </button>
          </div>
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
                  console.log('Param changed:', key, e.target.value);
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
const areEqual = (prevProps: ImageInputNodeProps, nextProps: ImageInputNodeProps) => {
  // 检查节点是否被选中
  if (prevProps.selected !== nextProps.selected) return false;
  
  // 检查节点数据的关键部分是否变化
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

export default React.memo(ImageInputNode as React.FC<ImageInputNodeProps>, areEqual);