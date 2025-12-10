import React, { useState } from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../types';


interface ControlNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const ControlNodeExample: React.FC<ControlNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  // 初始化控件状态
  const [controls, setControls] = useState<Record<string, any>>(() => {
    // 从data.params初始化控件值
    const initialControls: Record<string, any> = {};
    if (data.params) {
      Object.entries(data.params).forEach(([key, param]) => {
        const typedParam = param as NodeParam;
        initialControls[key] = typedParam.value;
      });
    }
    return initialControls;
  });

  // 计算最大连接点数量，用于CSS变量设置
  const inputCount = data.inputs?.length || 0;
  const outputCount = data.outputs?.length || 0;
  const maxHandleCount = Math.max(inputCount, outputCount);

  // 处理控件值变化
  const handleControlChange = (paramName: string, value: any) => {
    // 更新控件状态
    const newControls = { ...controls, [paramName]: value };
    setControls(newControls);
    
    // 更新节点数据
    if (onDataChange && data.params) {
      const updatedParams = { ...data.params };
      if (updatedParams[paramName]) {
        updatedParams[paramName].value = value;
      }
      
      onDataChange(nodeId || '', { ...data, params: updatedParams, controls: newControls });
    }
  };

  // 渲染不同类型的控件
  const renderControl = (param: NodeParam) => {
    const { name, label, type, options, step, widget_meta } = param;
    const value = controls[name];
    
    // 根据widget_meta或type渲染不同的控件
    if (widget_meta?.widget_type === 'slider' || type === 'number') {
      // 滑块控件
      return (
        <div className="control-group slider-control" key={name}>
          <label className="control-label">{label}</label>
          <input
            type="range"
            min={widget_meta?.min_value || 0}
            max={widget_meta?.max_value || 100}
            step={widget_meta?.step || step || 1}
            value={value || 0}
            onChange={(e) => handleControlChange(name, parseInt(e.target.value))}
            className="slider"
          />
          <span className="slider-value">{value || 0}</span>
        </div>
      );
    } else if (widget_meta?.widget_type === 'combo' || type === 'select') {
      // 下拉菜单控件
      return (
        <div className="control-group select-control" key={name}>
          <label className="control-label">{label}</label>
          <select
            value={value || ''}
            onChange={(e) => handleControlChange(name, e.target.value)}
            className="select"
          >
            <option value="">Select an option</option>
            {(options || widget_meta?.options || []).map((option: any, index: number) => (
              <option key={index} value={option.value || option}>
                {option.label || option}
              </option>
            ))}
          </select>
        </div>
      );
    } else if (widget_meta?.widget_type === 'toggle' || type === 'boolean') {
      // 开关控件
      return (
        <div className="control-group toggle-control" key={name}>
          <label className="control-label">{label}</label>
          <input
            type="checkbox"
            checked={value || false}
            onChange={(e) => handleControlChange(name, e.target.checked)}
            className="toggle"
          />
        </div>
      );
    } else {
      // 默认文本输入
      return (
        <div className="control-group text-control" key={name}>
          <label className="control-label">{label}</label>
          <input
            type="text"
            value={value || ''}
            onChange={(e) => handleControlChange(name, e.target.value)}
            className="node-input"
          />
        </div>
      );
    }
  };

  return (
    <div className="react-flow__node generic-node" style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label || 'Control Node'}</span>
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
        )}
      </div>
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        <div className="node-description">
          {data.description || 'A control node with multiple parameters'}
        </div>
        
        {/* 渲染所有参数控件 */}
        <div className="controls-container">
          {data.params && Object.values(data.params as Record<string, NodeParam>).map((param, index) => (
            <React.Fragment key={param.name || `param-${index}`}>
              {renderControl(param)}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ControlNodeExample;
