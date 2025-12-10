import React, { useState, useEffect } from 'react';
import { useI18n } from '../contexts/I18nContext';
import './ModelsManager.css';

// 模型类型定义
interface Model {
  name: string;
  type: string;
  path: string;
  size?: string;
  description?: string;
  preview?: string;
}

const ModelsManager: React.FC = () => {
  const { t } = useI18n();
  const [models, setModels] = useState<Model[]>([]);
  const [modelTypes, setModelTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [isDirectoryInfoExpanded, setIsDirectoryInfoExpanded] = useState<boolean>(false);

  // 获取模型类型
  useEffect(() => {
    const fetchModelTypes = async () => {
      try {
        console.log('Attempting to fetch model types...');
        const response = await fetch('http://127.0.0.1:8080/models/types', {
          mode: 'cors',
          cache: 'no-cache',
          credentials: 'same-origin',
          headers: {
            'Content-Type': 'application/json',
          },
          redirect: 'follow',
          referrerPolicy: 'no-referrer',
        });
        console.log('Model types response:', response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Model types data:', data);
        setModelTypes(data.model_types);
      } catch (err) {
        console.error('Error fetching model types:', err);
        setError(t('modelsManager.loadModelTypesError'));
      }
    };

    fetchModelTypes();
  }, [t]);

  // 获取模型列表
  useEffect(() => {
    const fetchModels = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log('Attempting to fetch models...');
        const url = selectedType === 'all' 
          ? 'http://127.0.0.1:8080/models' 
          : `http://127.0.0.1:8080/models?model_type=${selectedType}`;
        const response = await fetch(url, {
          mode: 'cors',
          cache: 'no-cache',
          credentials: 'same-origin',
          headers: {
            'Content-Type': 'application/json',
          },
          redirect: 'follow',
          referrerPolicy: 'no-referrer',
        });
        console.log('Models response:', response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Models data:', data);
        // 格式化模型数据
        const formattedModels: Model[] = data.models.map((model: any) => ({
          name: model.name,
          type: model.type,
          path: model.path,
          size: model.size,
        }));
        setModels(formattedModels);
      } catch (err) {
        console.error('Error fetching models:', err);
        setError('Failed to load models');
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, [selectedType, t]);

  // 搜索功能
  const filteredModels = models.filter(model => 
    model.name.toLowerCase().includes(searchQuery.toLowerCase())
  );



  // 删除模型处理
  const handleDelete = async (model: Model) => {
    if (!window.confirm(t('modelsManager.confirmDelete', { name: model.name }))) {
      return;
    }

    try {
      // 调用后端删除接口
      const encodedPath = encodeURIComponent(model.path);
      const url = `http://localhost:8080/models/delete?model_path=${encodedPath}`;
      console.log('Sending delete request to:', url);
      const response = await fetch(url, {
        method: 'DELETE',
      });

      const result = await response.json();
      if (!response.ok || result.status !== 'ok') {
        throw new Error(result.message || 'Failed to delete model');
      }

      // 从本地状态中移除删除的模型
      setModels(prevModels => prevModels.filter(m => m.path !== model.path));
      if (selectedModel?.path === model.path) {
        setSelectedModel(null);
      }
    } catch (err: any) {
      console.error('Error deleting model:', err);
      setError(t('modelsManager.deleteError', { message: err.message || 'Failed to delete model' }));
    }
  };

  // 查看模型详情
  const handleViewDetails = (model: Model) => {
    setSelectedModel(model);
  };

  return (
    <div className="models-manager">
      <div className="models-manager-header">
        <h2>{t('modelsManager.title')}</h2>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* 模型目录提示 */}
      <div className="model-directory-info">
        <div className="directory-info-header" onClick={() => setIsDirectoryInfoExpanded(!isDirectoryInfoExpanded)}>
          <p>{t('modelsManager.placeModelInfo')}</p>
          <span className={`expand-icon ${isDirectoryInfoExpanded ? 'expanded' : ''}`}>▼</span>
        </div>
        {isDirectoryInfoExpanded && (
          <div className="directory-info-content">
            <p>{t('modelsManager.modelDirectory')} <strong>uploads/models/</strong></p>
            <ul>
              <li>{t('modelTypes.base')}: <code>checkpoints/</code></li>
              <li>{t('modelTypes.lora')}: <code>loras/</code></li>
              <li>{t('modelTypes.vae')}: <code>vae/</code></li>
              <li>{t('modelTypes.text_encoder')}: <code>text_encoders/</code></li>
              <li>{t('modelTypes.clip_vision')}: <code>clip_vision/</code></li>
              <li>{t('modelTypes.controlnet')}: <code>controlnet/</code></li>
              <li>{t('modelTypes.embedding')}: <code>embeddings/</code></li>
              <li>{t('modelTypes.upscale')}: <code>upscale_models/</code></li>
            </ul>
          </div>
        )}
      </div>

      {/* 搜索和筛选 */}
      <div className="models-manager-controls">
        <input
          type="text"
          className="search-input"
          placeholder={t('modelsManager.search')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <select
          className="type-selector"
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
        >
          {modelTypes.map(type => (
            <option key={type} value={type}>
              {type === 'all' ? t('modelsManager.allTypes') : t(`modelTypes.${type}`)}
            </option>
          ))}
        </select>
      </div>

      {/* 模型列表 */}
      <div className="models-list-container">
        {loading ? (
          <div className="loading">{t('modelsManager.loading')}</div>
        ) : filteredModels.length === 0 ? (
          <div className="no-models">{t('modelsManager.noModels')}</div>
        ) : (
          <table className="models-list">
            <thead>
              <tr>
                <th>{t('modelsManager.name')}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filteredModels.map((model, index) => (
                <tr key={index} onClick={() => handleViewDetails(model)}>
                <td>{model.name}</td>
                <td className="model-actions">
                    <button 
                      className="delete-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(model);
                      }}
                    >
                      {t('modelsManager.delete')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* 模型详情 */}
      {selectedModel && (
        <div className="model-details">
          <div className="details-header">
            <h3>{selectedModel.name}</h3>
            <button 
              className="close-button"
              onClick={() => setSelectedModel(null)}
              title={t('modelsManager.close')}
            >
              ×
            </button>
          </div>
          <div className="details-content">
            <p><strong>{t('modelsManager.type')}：</strong>{selectedModel.type}</p>
            <p><strong>{t('modelsManager.path')}：</strong><span className="model-path-full">{selectedModel.path}</span></p>
            {selectedModel.size && <p><strong>{t('modelsManager.size')}：</strong>{selectedModel.size}</p>}
            {selectedModel.description && <p><strong>{t('modelsManager.description')}：</strong>{selectedModel.description}</p>}
            {selectedModel.preview && (
              <div className="model-preview">
                <h4>{t('modelsManager.preview')}：</h4>
                <img src={selectedModel.preview} alt="Model Preview" />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelsManager;