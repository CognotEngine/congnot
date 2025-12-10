import React from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../types';

interface PreviewOutputNodeProps {
  data: WorkflowNode['data'];
}

const PreviewOutputNodeExample: React.FC<PreviewOutputNodeProps> = ({ data }) => {

  // 从data中获取图像URL或Base64数据
  const imageUrl = data?.imageUrl || data?.preview;

  // 使用集中式布局计算手柄位置

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node generic-node" style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label || 'Image Preview Node'}</span>
      </div>
      
      {/* 连接区域 */}
      <div className="connection-area">
        {/* 左侧输入连接点 */}
        {data.inputs?.length > 0 && (
          <div className="handles-column left-handles">
            {data.inputs.map((input: NodeInput, index: number) => {
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
                    style={{ left: 0 }}
                  />
                  <span className="handle-label">{input.name}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* 中央内容占位符 */}
        <div className="central-content-placeholder"></div>

        {/* 右侧输出连接点 */}
        {data.outputs?.length > 0 && (
          <div className="handles-column right-handles">
            {data.outputs.map((output: NodeOutput, index: number) => {
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
                    style={{ right: 0 }}
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
        <div className="node-description">
          {data.description || 'A preview node for displaying images'}
        </div>
        
        {/* 图片预览区域 */}
        <div className="image-preview-container">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt="Preview"
              className="preview-image"
              onError={(e) => {
                console.error('Failed to load image:', e);
                // 可以在这里设置默认图片或错误状态
              }}
            />
          ) : (
            <div className="no-image-placeholder">
              <p>No image data available</p>
              <p>Connect an image source node</p>
            </div>
          )}
        </div>
        
        {/* 可选：保存按钮 */}
        {imageUrl && (
          <button 
            className="save-image-button"
            onClick={() => {
              // 实现保存图片逻辑
              if (imageUrl) {
                const link = document.createElement('a');
                link.href = imageUrl;
                link.download = 'preview-image.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }
            }}
          >
            Save Image
          </button>
        )}
      </div>
    </div>
  );
};

export default PreviewOutputNodeExample;
