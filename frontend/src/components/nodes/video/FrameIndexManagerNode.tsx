import React from 'react';
import { Handle, Position } from 'reactflow';
import { useI18n } from '../../../contexts/I18nContext';

interface FrameIndexManagerNodeProps {
  id: string;
  data: {
    currentFrame?: number;
    totalFrames?: number;
    isFirstFrame?: boolean;
    isLastFrame?: boolean;
    progress?: number;
  };
  onChange?: (id: string, data: any) => void;
}

const FrameIndexManagerNode: React.FC<FrameIndexManagerNodeProps> = ({ id, data, onChange }) => {
  const { t } = useI18n();
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  const handleTotalFramesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const totalFrames = parseInt(e.target.value) || 100;
    if (onChange) {
      onChange(id, {
        ...data,
        totalFrames,
        currentFrame: Math.min(data.currentFrame || 0, totalFrames - 1),
        isLastFrame: (data.currentFrame || 0) >= totalFrames - 1,
        progress: ((data.currentFrame || 0) / totalFrames) * 100,
      });
    }
  };

  const handleCurrentFrameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const currentFrame = parseInt(e.target.value) || 0;
    const totalFrames = data.totalFrames || 100;
    if (onChange) {
      onChange(id, {
        ...data,
        currentFrame: Math.min(Math.max(0, currentFrame), totalFrames - 1),
        isFirstFrame: currentFrame === 0,
        isLastFrame: currentFrame >= totalFrames - 1,
        progress: (currentFrame / totalFrames) * 100,
      });
    }
  };

  const handleReset = () => {
    if (onChange) {
      onChange(id, {
        ...data,
        currentFrame: 0,
        isFirstFrame: true,
        isLastFrame: false,
        progress: 0,
      });
    }
  };

  const handleNextFrame = () => {
    const currentFrame = data.currentFrame || 0;
    const totalFrames = data.totalFrames || 100;
    if (currentFrame < totalFrames - 1) {
      if (onChange) {
        onChange(id, {
          ...data,
          currentFrame: currentFrame + 1,
          isFirstFrame: false,
          isLastFrame: currentFrame + 1 >= totalFrames - 1,
          progress: ((currentFrame + 1) / totalFrames) * 100,
        });
      }
    }
  };

  return (
    <div className="video-node" onClick={handleNodeClick}>
      <div className="node-header">
        <h3>{t('nodePalette.Frame Index Manager')}</h3>
        <p>{t('nodePalette.Frame Index Manager description')}</p>
      </div>
      <Handle type="target" position={Position.Left} id="reset" style={{ background: '#555', top: '20px' }} />
      <Handle type="target" position={Position.Left} id="next" style={{ background: '#555', top: '45px' }} />
      <Handle type="source" position={Position.Right} id="frame_info" style={{ background: '#555', top: '20px' }} />
      <Handle type="source" position={Position.Right} id="progress" style={{ background: '#555', top: '45px' }} />
      <Handle type="source" position={Position.Right} id="flags" style={{ background: '#555', top: '70px' }} />
      <div className="node-content">
        <div className="parameter-group">
          <label>总帧数</label>
          <input type="number" min="1" max="10000" value={data.totalFrames || 100} onChange={handleTotalFramesChange} className="number-input" />
        </div>
        <div className="parameter-group">
          <label>当前帧</label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input type="number" min="0" max={data.totalFrames ? data.totalFrames - 1 : 99} value={data.currentFrame || 0} onChange={handleCurrentFrameChange} className="number-input flex-1" />
            <button onClick={handleReset} className="button small">重置</button>
            <button onClick={handleNextFrame} className="button small">下一帧</button>
          </div>
        </div>
        <div className="parameter-group">
          <label>进度</label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ flex: 1, height: '8px', backgroundColor: '#3a3a3a', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${data.progress || 0}%`, backgroundColor: '#666', transition: 'width 0.2s' }} />
            </div>
            <span style={{ color: '#c0c0c0', fontSize: '12px' }}>{Math.round(data.progress || 0)}%</span>
          </div>
        </div>
        <div className="parameter-group">
          <label>帧状态</label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ color: '#c0c0c0', fontSize: '12px' }}>首帧: <strong>{data.isFirstFrame ? '是' : '否'}</strong></span>
            <span style={{ color: '#c0c0c0', fontSize: '12px' }}>末帧: <strong>{data.isLastFrame ? '是' : '否'}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FrameIndexManagerNode;