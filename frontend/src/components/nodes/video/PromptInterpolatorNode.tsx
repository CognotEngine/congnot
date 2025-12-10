import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';

interface PromptInterpolatorNodeProps {
  id: string;
  data: {
    interpolationMethod?: string;
    strength?: number;
    smoothness?: number;
    prompts?: Array<{ frame: number; text: string }>;
    currentPrompt?: string;
  };
  onChange?: (id: string, data: any) => void;
}

const PromptInterpolatorNode: React.FC<PromptInterpolatorNodeProps> = ({ id, data, onChange }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  const [newPromptFrame, setNewPromptFrame] = useState<string>('0');
  const [newPromptText, setNewPromptText] = useState<string>('');

  const handleInterpolationMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (onChange) {
      onChange(id, { ...data, interpolationMethod: e.target.value });
    }
  };

  const handleStrengthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const strength = parseFloat(e.target.value) || 0.5;
    if (onChange) {
      onChange(id, { ...data, strength });
    }
  };

  const handleSmoothnessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const smoothness = parseFloat(e.target.value) || 1.0;
    if (onChange) {
      onChange(id, { ...data, smoothness });
    }
  };

  const handleAddPrompt = () => {
    const frame = parseInt(newPromptFrame) || 0;
    if (frame >= 0 && newPromptText.trim()) {
      const prompts = [...(data.prompts || []), { frame, text: newPromptText.trim() }];
      // 按帧排序
      prompts.sort((a, b) => a.frame - b.frame);
      if (onChange) {
        onChange(id, { ...data, prompts });
      }
      setNewPromptFrame('');
      setNewPromptText('');
    }
  };

  const handleRemovePrompt = (index: number) => {
    const prompts = [...(data.prompts || [])];
    prompts.splice(index, 1);
    if (onChange) {
      onChange(id, { ...data, prompts });
    }
  };

  return (
    <div className="video-node" onClick={handleNodeClick}>
      <div className="node-header">
        <h3>Prompt Interpolator</h3>
        <p>在视频序列中平滑插值提示文本</p>
      </div>
      <Handle type="target" position={Position.Left} id="frame_info" style={{ background: '#555' }} />
      <Handle type="source" position={Position.Right} id="interpolated_prompt" style={{ background: '#555' }} />
      <div className="node-content">
        <div className="parameter-group">
          <label>插值方法</label>
          <select value={data.interpolationMethod || 'linear'} onChange={handleInterpolationMethodChange} className="select-input">
            <option value="linear">线性</option>
            <option value="smoothstep">平滑</option>
            <option value="ease_in_out">缓进缓出</option>
            <option value="catmull_rom">Catmull-Rom</option>
          </select>
        </div>
        <div className="parameter-group">
          <label>插值强度</label>
          <div className="slider-input">
            <input type="range" min="0" max="1" step="0.01" value={data.strength || 0.5} onChange={handleStrengthChange} />
            <span>{(data.strength || 0.5).toFixed(2)}</span>
          </div>
        </div>
        <div className="parameter-group">
          <label>平滑度</label>
          <div className="slider-input">
            <input type="range" min="0" max="5" step="0.1" value={data.smoothness || 1.0} onChange={handleSmoothnessChange} />
            <span>{(data.smoothness || 1.0).toFixed(1)}</span>
          </div>
        </div>
        <div className="parameter-group">
          <label>添加关键帧提示</label>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <input
              type="number"
              min="0"
              placeholder="帧号"
              value={newPromptFrame}
              onChange={(e) => setNewPromptFrame(e.target.value)}
              className="number-input flex-1"
            />
            <button onClick={handleAddPrompt} className="button">添加</button>
          </div>
          <input
            type="text"
            placeholder="提示文本"
            value={newPromptText}
            onChange={(e) => setNewPromptText(e.target.value)}
            className="text-input"
            style={{ marginBottom: '8px' }}
          />
        </div>
        <div className="parameter-group">
          <label>关键帧提示列表</label>
          <div style={{ maxHeight: '150px', overflowY: 'auto', background: '#3a3a3a', border: '1px solid #555', borderRadius: '4px', padding: '8px' }}>
            {(data.prompts || []).map((prompt, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 0', borderBottom: '1px solid #555' }}>
                <div>
                  <span style={{ color: '#a0a0a0', fontSize: '10px' }}>帧 {prompt.frame}: </span>
                  <span style={{ color: '#e0e0e0', fontSize: '12px' }}>{prompt.text}</span>
                </div>
                <button onClick={() => handleRemovePrompt(index)} className="button" style={{ fontSize: '10px', padding: '2px 6px' }}>删除</button>
              </div>
            ))}
            {(!data.prompts || data.prompts.length === 0) && (
              <div style={{ textAlign: 'center', color: '#a0a0a0', fontSize: '12px' }}>无关键帧提示</div>
            )}
          </div>
        </div>
        <div className="parameter-group">
          <label>当前插值后提示</label>
          <div className="text-input" style={{ minHeight: '60px', fontSize: '12px', backgroundColor: '#3a3a3a', border: '1px solid #555' }}>
            {data.currentPrompt || '无'}</div>
        </div>
      </div>
    </div>
  );
};

export default PromptInterpolatorNode;