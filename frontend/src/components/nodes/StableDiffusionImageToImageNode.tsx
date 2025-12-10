import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../types';
import { getHandleColorByDataType } from '../../utils/handleColorUtils';
import { t } from '../../utils/i18n';

interface StableDiffusionImageToImageNodeProps extends NodeProps {
  data: WorkflowNode['data'];
}

const StableDiffusionImageToImageNode: React.FC<StableDiffusionImageToImageNodeProps> = ({ data }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  
  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  // 添加默认参数配置
  const defaultParams: Record<string, NodeParam> = {
    prompt: {
      name: 'prompt',
      label: t('nodePalette.prompt'),
      type: 'string',
      value: 'a beautiful landscape',
      widget_meta: {
        widget_type: 'text_input'
      }
    },
    negative_prompt: {
      name: 'negative_prompt',
      label: t('nodePalette.negativePrompt'),
      type: 'string',
      value: 'ugly, blurry',
      widget_meta: {
        widget_type: 'text_input'
      }
    },
    steps: {
      name: 'steps',
      label: t('nodePalette.generationSteps'),
      type: 'number',
      value: '20',
      widget_meta: {
        widget_type: 'number_input'
      }
    },
    cfg_scale: {
      name: 'cfg_scale',
      label: t('nodePalette.cfgScale'),
      type: 'number',
      value: '7',
      widget_meta: {
        widget_type: 'number_input'
      }
    },
    strength: {
      name: 'strength',
      label: t('nodePalette.strength'),
      type: 'number',
      value: '0.7',
      widget_meta: {
        widget_type: 'number_input'
      }
    }
  };

  // 使用传入的params或默认params，如果传入的params为空对象则使用默认params
  const params = Object.keys(data.params || {}).length > 0 ? data.params : defaultParams;

  return (
    <div 
      className={`react-flow__node generic-node`} 
      onClick={handleNodeClick}
      style={{ '--handle-count': maxHandleCount } as React.CSSProperties}
    >
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

        {/* 节点主体内容 */}
        <div className="central-content-placeholder">
          {/* 标题区域 */}
          <div className="node-header">
            <span>{data.label}</span>
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
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: StableDiffusionImageToImageNodeProps, nextProps: StableDiffusionImageToImageNodeProps) => {
  // 检查节点是否被选中
  if (prevProps.selected !== nextProps.selected) return false;
  
  // 检查图像数据是否变化
  if (prevProps.data.imageUrl !== nextProps.data.imageUrl) return false;
  if (prevProps.data.inputImageUrl !== nextProps.data.inputImageUrl) return false;
  
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

export default React.memo(StableDiffusionImageToImageNode as React.FC<StableDiffusionImageToImageNodeProps>, areEqual);
