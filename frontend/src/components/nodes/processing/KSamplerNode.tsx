import React from 'react';
import { Handle, Position, useNodeId, NodeProps } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';
import { t } from '../../../utils/i18n';

interface KSamplerNodeProps extends NodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const KSamplerNode: React.FC<KSamplerNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
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

  // 常用采样器类型
  const samplerTypes = ['Euler', 'Euler a', 'DPM++ 2M', 'DPM++ 2M Karras', 'DPM++ SDE', 'DPM++ SDE Karras', 'DDIM', 'PLMS'];
  
  // 常用调度器类型
  const schedulerTypes = ['normal', 'karras', 'exponential', 'polyexponential', 'ddim_uniform'];
  
  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div 
      className="react-flow__node k-sampler-node"
      onClick={handleNodeClick}
      style={{ '--handle-count': maxHandleCount } as React.CSSProperties}
    >
      {/* 连接区域 */}
      <div className="connection-area">
        {/* 左侧输入连接点 */}
        {data.inputs?.length > 0 && (
          <div className="handles-column left-handles">
            {data.inputs.map((input: NodeInput, index: number) => {
              const handleId = input.id || input.name || `input-${index}`;
              return (
                <div key={handleId} className="handle-item">
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
          <div className="node-header">
            <span>{data.label}</span>
          </div>
          <div className="node-content">
            <div className="param-group">
              <label className="param-label">{t('nodePalette.steps')}</label>
              <input
                type="number"
                value={data.params?.steps?.value || 20}
                min="1"
                max="100"
                step="1"
                className="node-input"
                onChange={(e) => {
                  handleParamChange('steps', parseInt(e.target.value));
                }}
              />
            </div>
            
            <div className="param-group">
              <label className="param-label">{t('nodePalette.cfgScale')}</label>
              <input
                type="number"
                value={data.params?.cfgScale?.value || 7}
                min="1"
                max="30"
                step="0.1"
                className="node-input"
                onChange={(e) => {
                  handleParamChange('cfgScale', parseFloat(e.target.value));
                }}
              />
            </div>
            
            <div className="param-group">
              <label className="param-label">{t('nodePalette.sampler')}</label>
              <select
                value={data.params?.sampler?.value || 'Euler a'}
                className="node-input"
                onChange={(e) => {
                  handleParamChange('sampler', e.target.value);
                }}
              >
                {samplerTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="param-group">
              <label className="param-label">{t('nodePalette.scheduler')}</label>
              <select
                value={data.params?.scheduler?.value || 'karras'}
                className="node-input"
                onChange={(e) => {
                  handleParamChange('scheduler', e.target.value);
                }}
              >
                {schedulerTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="param-group">
              <label className="param-label">{t('nodePalette.seed')}</label>
              <input
                type="number"
                value={data.params?.seed?.value || -1}
                className="node-input"
                onChange={(e) => {
                  handleParamChange('seed', parseInt(e.target.value));
                }}
              />
            </div>
            
            {Object.entries(data.params || {}).map(([key, param]) => {
              if (!['steps', 'cfgScale', 'sampler', 'scheduler', 'seed'].includes(key)) {
                const typedParam = param as NodeParam;
                return (
                  <div key={key} className="param-group">
                    <label className="param-label">{typedParam.label}</label>
                    <input
                      type={typedParam.type}
                      value={typedParam.value}
                      className="node-input"
                      onChange={(e) => {
                        handleParamChange(key, typedParam.type === 'number' ? parseFloat(e.target.value) : e.target.value);
                      }}
                    />
                  </div>
                );
              }
              return null;
            })}
          </div>
        </div>

        {/* 右侧输出连接点 */}
        {data.outputs?.length > 0 && (
          <div className="handles-column right-handles">
            {data.outputs.map((output: NodeOutput, index: number) => {
              const handleId = output.id || output.name || `output-${index}`;
              return (
                <div key={handleId} className="handle-item">
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

export default KSamplerNode;