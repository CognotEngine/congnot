import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeOutput, NodeParam } from '../../types';
import { getHandleColorByDataType } from '../../utils/handleColorUtils';
import { t } from '../../utils/i18n';

import { NodeProps } from 'reactflow';

interface TextInputNodeProps extends NodeProps {
  data: WorkflowNode['data'];
}

const TextInputNode: React.FC<TextInputNodeProps> = ({ data, selected }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  // 添加默认参数配置
  const defaultParams: Record<string, NodeParam> = {
    text: {
      name: 'text',
      label: t('nodePalette.textContent'),
      type: 'string',
      value: '输入文本内容',
      widget_meta: {
        widget_type: 'text_input'
      }
    }
  };


  // 使用传入的params或默认params
  const params = data.params || defaultParams;

  return (
    <div className={`react-flow__node generic-node ${selected ? 'selected' : ''}`} onClick={handleNodeClick}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label || 'Text Input'}</span>
      </div>
      
      {/* Connection area with labeled handles */}
      <div className="connection-area">
        {/* Left handles column */}
        <div className="handles-column left-handles">
          {/* TextInputNode没有输入连接点 */}
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
      <div className="node-content">
        {Object.entries(params).map(([key, param]) => {
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

export default memo(TextInputNode);
