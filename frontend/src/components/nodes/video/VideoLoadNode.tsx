import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';
import { useI18n } from '../../../contexts/I18nContext';

interface VideoLoadNodeProps {
  id: string;
  data: {
    videoPath?: string;
    frameRate?: number;
    totalFrames?: number;
    resolution?: { width: number; height: number };
  };
  onChange?: (id: string, data: any) => void;
}

const VideoLoadNode: React.FC<VideoLoadNodeProps> = ({ id, data, onChange }) => {
  const { t } = useI18n();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (onChange) {
        onChange(id, {
          ...data,
          videoPath: file.name,
          // Extract video metadata would go here in a real implementation
        });
      }
    }
  };

  const handleFrameRateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(id, {
        ...data,
        frameRate: parseInt(e.target.value) || 24,
      });
    }
  };

  const handleTotalFramesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(id, {
        ...data,
        totalFrames: parseInt(e.target.value) || 100,
      });
    }
  };

  const handleWidthChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(id, {
        ...data,
        resolution: {
          ...data.resolution,
          width: parseInt(e.target.value) || 1024,
        },
      });
    }
  };

  const handleHeightChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(id, {
        ...data,
        resolution: {
          ...data.resolution,
          height: parseInt(e.target.value) || 512,
        },
      });
    }
  };

  return (
    <div className="video-node" onClick={handleNodeClick}>
      <div className="node-header">
        <h3>{t('nodePalette.Video/Image Load')}</h3>
        <p>{t('nodePalette.Video/Image Load description')}</p>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="video_output"
        style={{ background: '#555', top: '20px' }}
      />
      
      <div className="node-content">
        <div className="parameter-group">
          <label>视频文件</label>
          <input
            type="file"
            accept="video/*,image/*"
            onChange={handleFileChange}
            className="file-input"
          />
          {selectedFile && (
            <div className="file-info">
              <span>{selectedFile.name}</span>
            </div>
          )}
        </div>
        
        <div className="parameter-group">
          <label>帧率</label>
          <input
            type="number"
            min="1"
            max="60"
            value={data.frameRate || 24}
            onChange={handleFrameRateChange}
            className="number-input"
          />
        </div>
        
        <div className="parameter-group">
          <label>总帧数</label>
          <input
            type="number"
            min="1"
            max="10000"
            value={data.totalFrames || 100}
            onChange={handleTotalFramesChange}
            className="number-input"
          />
        </div>
        
        <div className="parameter-group">
          <label>分辨率</label>
          <div className="resolution-inputs">
            <input
              type="number"
              min="64"
              max="4096"
              value={data.resolution?.width || 1024}
              onChange={handleWidthChange}
              placeholder="宽度"
              className="number-input small"
            />
            <span>x</span>
            <input
              type="number"
              min="64"
              max="4096"
              value={data.resolution?.height || 512}
              onChange={handleHeightChange}
              placeholder="高度"
              className="number-input small"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoLoadNode;