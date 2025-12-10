import React from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface PreviewNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
  selected?: boolean;
}

const PreviewNode: React.FC<PreviewNodeProps> = ({ data }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  
  // 计算最大连接数，用于设置连接区域高度
  const maxHandleCount = Math.max(
    data.inputs?.length || 0,
    data.outputs?.length || 0
  );
  


  return (
    <div className="react-flow__node generic-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
      {/* 连接区域 */}
      <div className="connection-area">
        {/* 左侧输入连接点 */}
        {data.inputs?.length > 0 && (
          <div className="handles-column left-handles">
            {data.inputs.map((input: NodeInput, index: number) => {
              const handleKey = input.id || input.name || `input-${index}`;
              return (
                <div key={handleKey} className="handle-item">
                  <Handle
                    id={handleKey}
                    type="target"
                    position={Position.Left}
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
        )}

        {/* 节点主体内容 */}
        <div className="central-content-placeholder">
          {/* 标题区域 */}
          <div className="node-header">
            <span>{data.label}</span>
          </div>
        </div>

        {/* 右侧输出连接点 */}
        {data.outputs?.length > 0 && (
          <div className="handles-column right-handles">
            {data.outputs.map((output: NodeOutput, index: number) => {
              const handleKey = output.id || output.name || `output-${index}`;
              return (
                <div key={handleKey} className="handle-item">
                  <Handle
                    id={handleKey}
                    type="source"
                    position={Position.Right}
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
        )}
      </div>
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        <div className="image-preview-container">
          {data.imageUrl ? (
            <img
              src={data.imageUrl}
              alt="Preview image"
              className="node-image-preview"
              style={{ maxHeight: '200px', maxWidth: '100%' }}
            />
          ) : (
            <div className="image-placeholder">
              <span>Preview Image</span>
            </div>
          )}
        </div>
        
        <div className="preview-controls">
          <button
            className="save-image-button"
            onClick={() => {
              console.log('Refresh preview');
            }}
          >
            Refresh
          </button>
          <button
            className="save-image-button"
            onClick={() => {
              console.log('Zoom in');
            }}
          >
            Zoom In
          </button>
          <button
            className="save-image-button"
            onClick={() => {
              console.log('Zoom out');
            }}
          >
            Zoom Out
          </button>
        </div>
      </div>
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: PreviewNodeProps, nextProps: PreviewNodeProps) => {
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

export default React.memo(PreviewNode as React.FC<PreviewNodeProps>, areEqual);