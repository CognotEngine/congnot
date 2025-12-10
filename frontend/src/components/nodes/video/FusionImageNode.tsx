import React from 'react';
import { Handle, Position } from 'reactflow';

interface FusionImageNodeProps {
  id: string;
  data: {
    fusionMethod?: string;
    alpha?: number;
    maskSmoothness?: number;
    preserveDetails?: boolean;
    detailPreservationLevel?: number;
  };
  onChange?: (id: string, data: any) => void;
}

const FusionImageNode: React.FC<FusionImageNodeProps> = ({ id, data, onChange }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  const handleFusionMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (onChange) {
      onChange(id, { ...data, fusionMethod: e.target.value });
    }
  };

  const handleAlphaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const alpha = parseFloat(e.target.value) || 0.5;
    if (onChange) {
      onChange(id, { ...data, alpha });
    }
  };

  const handleMaskSmoothnessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const maskSmoothness = parseFloat(e.target.value) || 1.0;
    if (onChange) {
      onChange(id, { ...data, maskSmoothness });
    }
  };

  const handlePreserveDetailsToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(id, { ...data, preserveDetails: e.target.checked });
    }
  };

  const handleDetailLevelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const detailPreservationLevel = parseFloat(e.target.value) || 0.5;
    if (onChange) {
      onChange(id, { ...data, detailPreservationLevel });
    }
  };

  return (
    <div className="video-node" onClick={handleNodeClick}>
      <div className="node-header">
        <h3>Fusion Image</h3>
        <p>将AI生成的图像与原始图像融合，保持连续性和细节</p>
      </div>
      <Handle type="target" position={Position.Left} id="generated_image" style={{ background: '#555' }} />
      <Handle type="target" position={Position.Left} id="original_image" style={{ background: '#555', top: '30%' }} />
      <Handle type="target" position={Position.Left} id="fusion_mask" style={{ background: '#555', top: '70%' }} />
      <Handle type="source" position={Position.Right} id="fused_image" style={{ background: '#555' }} />
      <div className="node-content">
        <div className="parameter-group">
          <label>融合方法</label>
          <select value={data.fusionMethod || 'alpha_blend'} onChange={handleFusionMethodChange} className="select-input">
            <option value="alpha_blend">Alpha 混合</option>
            <option value="masked_blend">遮罩混合</option>
            <option value="laplacian">拉普拉斯金字塔</option>
            <option value="gradient">梯度混合</option>
          </select>
        </div>
        <div className="parameter-group">
          <label>混合比例</label>
          <div className="slider-input">
            <input type="range" min="0" max="1" step="0.01" value={data.alpha || 0.5} onChange={handleAlphaChange} />
            <span>{(data.alpha || 0.5).toFixed(2)}</span>
          </div>
        </div>
        <div className="parameter-group">
          <label>遮罩平滑度</label>
          <div className="slider-input">
            <input type="range" min="0" max="5" step="0.1" value={data.maskSmoothness || 1.0} onChange={handleMaskSmoothnessChange} />
            <span>{(data.maskSmoothness || 1.0).toFixed(1)}</span>
          </div>
        </div>
        <div className="parameter-group">
          <div className="checkbox-input">
            <input type="checkbox" id="preserve_details" checked={data.preserveDetails || false} onChange={handlePreserveDetailsToggle} />
            <label htmlFor="preserve_details">保留细节</label>
          </div>
        </div>
        {data.preserveDetails && (
          <div className="parameter-group" style={{ marginLeft: '24px' }}>
            <label>细节保留级别</label>
            <div className="slider-input">
              <input type="range" min="0" max="1" step="0.01" value={data.detailPreservationLevel || 0.5} onChange={handleDetailLevelChange} />
              <span>{(data.detailPreservationLevel || 0.5).toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FusionImageNode;