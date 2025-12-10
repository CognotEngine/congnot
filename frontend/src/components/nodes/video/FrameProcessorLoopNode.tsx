import React from 'react';
import { Handle, Position } from 'reactflow';

interface FrameProcessorLoopNodeProps {
  id: string;
  data: {
    iterations?: number;
    denoiseStrength?: number;
    guidanceScale?: number;
    seed?: number;
    useMotionBlending?: boolean;
    motionBlendingStrength?: number;
  };
  onChange?: (id: string, data: any) => void;
}

const FrameProcessorLoopNode: React.FC<FrameProcessorLoopNodeProps> = ({ id, data, onChange }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  const handleIterationsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const iterations = parseInt(e.target.value) || 50;
    if (onChange) {
      onChange(id, { ...data, iterations });
    }
  };

  const handleDenoiseChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const denoiseStrength = parseFloat(e.target.value) || 0.7;
    if (onChange) {
      onChange(id, { ...data, denoiseStrength });
    }
  };

  const handleGuidanceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const guidanceScale = parseFloat(e.target.value) || 7.5;
    if (onChange) {
      onChange(id, { ...data, guidanceScale });
    }
  };

  const handleSeedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const seed = parseInt(e.target.value) || -1;
    if (onChange) {
      onChange(id, { ...data, seed });
    }
  };

  const handleMotionBlendingToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(id, { ...data, useMotionBlending: e.target.checked });
    }
  };

  const handleMotionBlendingStrengthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const motionBlendingStrength = parseFloat(e.target.value) || 0.5;
    if (onChange) {
      onChange(id, { ...data, motionBlendingStrength });
    }
  };

  return (
    <div className="video-node" onClick={handleNodeClick}>
      <div className="node-header">
        <h3>Frame Processor Loop</h3>
        <p>迭代处理视频中的每一帧并应用AI生成</p>
      </div>
      <Handle type="target" position={Position.Left} id="initial_frame" style={{ background: '#555', top: '20px' }} />
      <Handle type="target" position={Position.Left} id="prompt" style={{ background: '#555', top: '45px' }} />
      <Handle type="target" position={Position.Left} id="flow_field" style={{ background: '#555', top: '70px' }} />
      <Handle type="source" position={Position.Right} id="generated_frame" style={{ background: '#555', top: '20px' }} />
      <Handle type="source" position={Position.Right} id="latent_output" style={{ background: '#555', top: '45px' }} />
      <div className="node-content">
        <div className="parameter-group">
          <label>采样迭代次数</label>
          <input type="number" min="1" max="200" value={data.iterations || 50} onChange={handleIterationsChange} className="number-input" />
        </div>
        <div className="parameter-group">
          <label>去噪强度</label>
          <div className="slider-input">
            <input type="range" min="0" max="1" step="0.01" value={data.denoiseStrength || 0.7} onChange={handleDenoiseChange} />
            <span>{(data.denoiseStrength || 0.7).toFixed(2)}</span>
          </div>
        </div>
        <div className="parameter-group">
          <label>引导缩放</label>
          <div className="slider-input">
            <input type="range" min="0" max="20" step="0.1" value={data.guidanceScale || 7.5} onChange={handleGuidanceChange} />
            <span>{(data.guidanceScale || 7.5).toFixed(1)}</span>
          </div>
        </div>
        <div className="parameter-group">
          <label>随机种子</label>
          <input type="number" min="-1" max="999999999" value={data.seed || -1} onChange={handleSeedChange} className="number-input" placeholder="-1 表示随机" />
        </div>
        <div className="parameter-group">
          <div className="checkbox-input">
            <input type="checkbox" id="motion_blending" checked={data.useMotionBlending || false} onChange={handleMotionBlendingToggle} />
            <label htmlFor="motion_blending">启用运动融合</label>
          </div>
        </div>
        {data.useMotionBlending && (
          <div className="parameter-group" style={{ marginLeft: '24px' }}>
            <label>运动融合强度</label>
            <div className="slider-input">
              <input type="range" min="0" max="1" step="0.01" value={data.motionBlendingStrength || 0.5} onChange={handleMotionBlendingStrengthChange} />
              <span>{(data.motionBlendingStrength || 0.5).toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FrameProcessorLoopNode;