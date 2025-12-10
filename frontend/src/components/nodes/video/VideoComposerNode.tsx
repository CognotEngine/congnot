import React from 'react';
import { Handle, Position, useNodeId } from 'reactflow';
import { WorkflowNode } from '../../../types';

interface VideoComposerNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const VideoComposerNode: React.FC<VideoComposerNodeProps> = ({ data, onDataChange }) => {
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
  
  const handleFormatChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    handleParamChange('outputFormat', e.target.value);
  };

  const handleFPSChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fps = parseInt(e.target.value) || 24;
    handleParamChange('fps', fps);
  };

  const handleBitrateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleParamChange('bitrate', e.target.value);
  };

  const handleCodecChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    handleParamChange('codec', e.target.value);
  };

  const handleOutputPathChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleParamChange('outputPath', e.target.value);
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  return (
    <div className="video-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as unknown as React.CSSProperties}>
      <div className="node-header">
        <h3>Video Composer</h3>
        <p>将一系列帧合成最终视频</p>
      </div>
      {/* 连接区域 */}
      <div className="connection-area">
        {/* Input handles with labels */}
        <div className="handles-column left-handles">
          <div className="handle-item">
            <Handle type="target" position={Position.Left} id="frames" style={{ background: '#555', left: 0 }} />
            <span className="handle-label">frames</span>
          </div>
        </div>
        
        {/* Central content placeholder */}
        <div className="central-content-placeholder"></div>
        
        {/* Output handles with labels */}
        <div className="handles-column right-handles">
          <div className="handle-item">
            <Handle type="source" position={Position.Right} id="video" style={{ background: '#555', right: 0 }} />
            <span className="handle-label">video</span>
          </div>
        </div>
      </div>
      <div className="node-content">
        <div className="parameter-group">
          <label>输出格式</label>
          <select value={data.params?.outputFormat?.value || 'mp4'} onChange={handleFormatChange} className="select-input">
            <option value="mp4">MP4</option>
            <option value="webm">WebM</option>
            <option value="avi">AVI</option>
            <option value="mov">MOV</option>
          </select>
        </div>
        <div className="parameter-group">
          <label>帧率 (FPS)</label>
          <input type="number" min="1" max="60" value={data.params?.fps?.value || 24} onChange={handleFPSChange} className="number-input" />
        </div>
        <div className="parameter-group">
          <label>比特率</label>
          <input type="text" value={data.params?.bitrate?.value || '10M'} onChange={handleBitrateChange} className="text-input" placeholder="例如: 10M, 8000k" />
        </div>
        <div className="parameter-group">
          <label>视频编码</label>
          <select value={data.params?.codec?.value || 'h264'} onChange={handleCodecChange} className="select-input">
            <option value="h264">H.264</option>
            <option value="h265">H.265</option>
            <option value="vp9">VP9</option>
            <option value="av1">AV1</option>
          </select>
        </div>
        <div className="parameter-group">
          <label>输出路径</label>
          <input type="text" value={data.params?.outputPath?.value || ''} onChange={handleOutputPathChange} className="text-input" placeholder="视频保存路径" />
        </div>
        <button className="button" style={{ marginTop: '8px' }}>预览视频</button>
      </div>
    </div>
  );
};

export default VideoComposerNode;