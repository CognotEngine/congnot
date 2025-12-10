import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode } from '../../../types';

interface OpticalFlowCalculatorNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const OpticalFlowCalculatorNode: React.FC<OpticalFlowCalculatorNodeProps> = ({ data, onDataChange }) => {
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
      } else {
        // 如果参数不存在，则创建它
        updatedParams[paramName] = { value, type: typeof value };
      }
      
      onDataChange(nodeId || '', { ...data, params: updatedParams });
    }
  };
  
  const handleMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    handleParamChange('method', e.target.value);
  };

  const handleQualityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    handleParamChange('quality', e.target.value);
  };

  const handleMaxFlowChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const maxFlow = parseInt(e.target.value) || 20;
    handleParamChange('maxFlow', maxFlow);
  };

  const handleVisualizationToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleParamChange('showVisualization', e.target.checked);
  };

  return (
    <div className="video-node" onClick={handleNodeClick}>
      <div className="node-header">
        <h3>Optical Flow Calculator</h3>
        <p>检测帧之间的运动并生成光流场</p>
      </div>
      <Handle type="target" position={Position.Left} id="prev_frame" style={{ background: '#555' }} />
      <Handle type="target" position={Position.Left} id="current_frame" style={{ background: '#555', top: '30%' }} />
      <Handle type="source" position={Position.Right} id="flow_field" style={{ background: '#555' }} />
      <Handle type="source" position={Position.Right} id="motion_mask" style={{ background: '#555', top: '30%' }} />
      <Handle type="source" position={Position.Right} id="visualization" style={{ background: '#555', top: '70%' }} />
      <div className="node-content">
        <div className="parameter-group">
          <label>计算方法</label>
          <select value={data.params?.method?.value || 'farneback'} onChange={handleMethodChange} className="select-input">
            <option value="farneback">Farneback</option>
            <option value="lucas_kanade">Lucas-Kanade</option>
            <option value="dense">Dense</option>
          </select>
        </div>
        <div className="parameter-group">
          <label>质量设置</label>
          <select value={data.params?.quality?.value || 'medium'} onChange={handleQualityChange} className="select-input">
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
          </select>
        </div>
        <div className="parameter-group">
          <label>最大流量值</label>
          <input type="number" min="1" max="100" value={data.params?.maxFlow?.value || 20} onChange={handleMaxFlowChange} className="number-input" />
        </div>
        <div className="parameter-group">
          <div className="checkbox-input">
            <input type="checkbox" id="visualize" checked={data.params?.showVisualization?.value || false} onChange={handleVisualizationToggle} />
            <label htmlFor="visualize">显示可视化</label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpticalFlowCalculatorNode;