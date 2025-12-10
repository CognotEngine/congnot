import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../../types';
import { getHandleColorByDataType } from '../../../utils/handleColorUtils';

interface ImageManipulationNodeProps {
  data: WorkflowNode['data'];
  onDataChange: (nodeId: string, updatedData: Partial<WorkflowNode['data']>) => void;
}

const ImageManipulationNode: React.FC<ImageManipulationNodeProps> = ({ data, onDataChange }) => {
  const nodeId = useNodeId();
  
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  const handleParamChange = (paramName: string, value: string | number | boolean) => {
    onDataChange(nodeId || '', {
      params: {
        ...data.params,
        [paramName]: {
          ...data.params?.[paramName],
          value
        }
      }
    });
  };

  // 图像操作类型
  const manipulationTypes = ['Resize', 'Crop', 'Blend', 'Enhance'];
  
  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="react-flow__node generic-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
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
            return (
              <div key={handleKey} className="handle-item">
                <Handle
                  type="target"
                  position={Position.Left}
                  id={`${handleKey}-handle`}
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
        
        {/* Central content placeholder */}
        <div className="central-content-placeholder"></div>
        
        {/* Output handles with labels */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput, index: number) => {
            const handleKey = output.id || output.name || `output-${index}`;
            return (
              <div key={handleKey} className="handle-item">
                <Handle
                  type="source"
                  position={Position.Right}
                  id={`${handleKey}-handle`}
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
      </div>
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        <div className="param-group">
          <label className="param-label">Operation</label>
          <select
            value={data.params?.operation?.value || 'Resize'}
            className="node-input"
            onChange={(e) => {
              handleParamChange('operation', e.target.value);
            }}
          >
            {manipulationTypes.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
        
        <div className="param-group">
          <label className="param-label">Width</label>
          <input
            type="number"
            value={data.params?.width?.value || 512}
            min="64"
            max="8192"
            step="1"
            className="node-input"
            onChange={(e) => {
              handleParamChange('width', parseInt(e.target.value) || 512);
            }}
          />
        </div>
        
        <div className="param-group">
          <label className="param-label">Height</label>
          <input
            type="number"
            value={data.params?.height?.value || 512}
            min="64"
            max="8192"
            step="1"
            className="node-input"
            onChange={(e) => {
              handleParamChange('height', parseInt(e.target.value) || 512);
            }}
          />
        </div>
        
        <div className="param-group">
          <label className="param-label">Blend Mode</label>
          <select
            value={data.params?.blendMode?.value || 'Normal'}
            className="node-input"
            onChange={(e) => {
              handleParamChange('blendMode', e.target.value);
            }}
          >
            <option key="Normal" value="Normal">Normal</option>
            <option key="Multiply" value="Multiply">Multiply</option>
            <option key="Screen" value="Screen">Screen</option>
            <option key="Overlay" value="Overlay">Overlay</option>
            <option key="Lighten" value="Lighten">Lighten</option>
            <option key="Darken" value="Darken">Darken</option>
            <option key="Color Dodge" value="Color Dodge">Color Dodge</option>
            <option key="Color Burn" value="Color Burn">Color Burn</option>
          </select>
        </div>
        
        <div className="param-group">
          <label className="param-label">Opacity</label>
          <input
            type="number"
            value={data.params?.opacity?.value || 1.0}
            min="0"
            max="1"
            step="0.1"
            className="node-input"
            onChange={(e) => {
              handleParamChange('opacity', parseFloat(e.target.value) || 1.0);
            }}
          />
        </div>
        
        {Object.entries(data.params || {}).map(([key, param]) => {
          if (!['operation', 'width', 'height', 'blendMode', 'opacity'].includes(key)) {
            const typedParam = param as NodeParam;
            return (
              <div key={key} className="param-group">
                <label className="param-label">{typedParam.label}</label>
                <input
                  type={typedParam.type}
                  value={typedParam.value}
                  className="node-input"
                  onChange={(e) => {
                    const value = typedParam.type === 'number' 
                      ? parseFloat(e.target.value) || 0
                      : e.target.value;
                    handleParamChange(key, value);
                  }}
                />
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

export default ImageManipulationNode;