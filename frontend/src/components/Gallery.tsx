import React, { useState, useEffect } from 'react'
import './Gallery.css'
import { useI18n } from '../contexts/I18nContext'

interface FileItem {
  filename: string;
  file_type: 'image' | 'audio' | 'video' | 'document' | 'other';
  content_type: string;
  file_size: number;
  upload_time: number;
  storage_path: string;
  relative_path: string;
}

interface GalleryProps {
  onSelectFile?: (file: FileItem) => void;
}

const Gallery = ({ onSelectFile }: GalleryProps) => {
  const { t } = useI18n();
  const [files, setFiles] = useState<FileItem[]>([])
  const [filteredFiles, setFilteredFiles] = useState<FileItem[]>([])
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [fileTypeFilter, setFileTypeFilter] = useState<'all' | 'image' | 'audio' | 'video' | 'document'>('all') 
  const [uploading, setUploading] = useState<boolean>(false)
  const [searchQuery, setSearchQuery] = useState<string>('')

  
  const loadFiles = async (): Promise<void> => {
    try {
      const response = await fetch('/files/list')
      const data = await response.json()
      if (data.files) {
        setFiles(data.files)
        setFilteredFiles(data.files)
      }
    } catch (error) {
      console.error('Failed to load files:', error)
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  
  useEffect(() => {
    let result = [...files]
    
    
    if (fileTypeFilter !== 'all') {
      result = result.filter(file => file.file_type === fileTypeFilter)
    }
    
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(file => 
        file.filename.toLowerCase().includes(query) ||
        file.content_type.toLowerCase().includes(query)
      )
    }
    
    setFilteredFiles(result)
  }, [fileTypeFilter, searchQuery, files])

  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch('/files/upload', {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        
        loadFiles()
      } else {
        console.error('File upload failed')
      }
    } catch (error) {
      console.error('File upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  
  const handleFileDelete = async (file: FileItem): Promise<void> => {
    if (!window.confirm(`Are you sure you want to delete "${file.filename}"?`)) {
      return
    }

    try {
      const response = await fetch(`/files/delete?filename=${file.filename}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        
        loadFiles()
        
        if (selectedFile && selectedFile.storage_path === file.storage_path) {
          setSelectedFile(null)
        }
      } else {
        console.error('File deletion failed')
      }
    } catch (error) {
      console.error('File deletion error:', error)
    }
  }

  
  const handleFileSelect = (file: FileItem): void => {
    setSelectedFile(file)
    if (onSelectFile) {
      onSelectFile(file)
    }
  }

  
  const handleFileDownload = (file: FileItem): void => {
    window.open(`/files/download?filename=${file.filename}`)
  }

  
  const getFileIcon = (file: FileItem): React.ReactNode => {
    const { file_type, content_type } = file
    
    switch (file_type) {
      case 'image':
        return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      case 'audio':
        return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
      case 'video':
        return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
      case 'document':
        if (content_type.includes('pdf')) return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        if (content_type.includes('word')) return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        if (content_type.includes('excel') || content_type.includes('csv')) return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
        if (content_type.includes('text') || content_type.includes('json') || content_type.includes('javascript')) return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      default:
        return <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="12" cy="12" r="3"/></svg>
    }
  }

  
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  
  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp * 1000) 
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="gallery-container">
      <div className="gallery-header">
        <h3>{t('gallery.title')}</h3>
        <div className="gallery-controls">
          <label htmlFor="file-upload" className="button">
            <svg className="svgIcon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg> {t('gallery.upload')}
          </label>
          <input 
            id="file-upload" 
            type="file" 
            onChange={handleFileUpload} 
            style={{ display: 'none' }}
            disabled={uploading}
          />
        </div>
      </div>

      <div className="gallery-toolbar">
        <div className="search-bar">
          <input 
            type="text" 
            placeholder={t('gallery.searchPlaceholder')} 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="file-type-filters">
          <button 
            className={`filter-btn ${fileTypeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setFileTypeFilter('all')}
          >
            {t('gallery.all')}
          </button>
          <button 
            className={`filter-btn ${fileTypeFilter === 'image' ? 'active' : ''}`}
            onClick={() => setFileTypeFilter('image')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg> {t('gallery.images')}
          </button>
          <button 
            className={`filter-btn ${fileTypeFilter === 'audio' ? 'active' : ''}`}
            onClick={() => setFileTypeFilter('audio')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg> {t('gallery.audio')}
          </button>
          <button 
            className={`filter-btn ${fileTypeFilter === 'video' ? 'active' : ''}`}
            onClick={() => setFileTypeFilter('video')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg> {t('gallery.videos')}
          </button>
          <button 
            className={`filter-btn ${fileTypeFilter === 'document' ? 'active' : ''}`}
            onClick={() => setFileTypeFilter('document')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg> {t('gallery.documents')}
          </button>
        </div>
      </div>

      <div className="gallery-content">
        {filteredFiles.length === 0 ? (
          <div className="no-files">
            <p>{uploading ? t('gallery.uploading') : t('gallery.noFiles')}</p>
          </div>
        ) : (
          <div className="files-grid">
            {filteredFiles.map((file, index) => (
              <div 
                key={index} 
                className={`file-item ${selectedFile?.storage_path === file.storage_path ? 'selected' : ''}`}
                onClick={() => handleFileSelect(file)}
              >
                <div className="file-icon">
                  {file.file_type === 'image' ? (
                    <img 
                      src={`/files/preview?filename=${file.filename}`}
                      alt={file.filename} 
                      className="file-thumbnail"
                    />
                  ) : (
                    <div className="icon-svg">{getFileIcon(file)}</div>
                  )}
                </div>
                <div className="file-info">
                  <div className="file-name">{file.filename}</div>
                  <div className="file-meta">
                    <span className="file-size">{formatFileSize(file.file_size)}</span>
                    <span className="file-date">{formatDate(file.upload_time)}</span>
                  </div>
                </div>
                <div className="file-actions">
                  <button 
                    className="action-btn download-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleFileDownload(file)
                    }}
                    title={t('common.download')}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  </button>
                  <button 
                    className="action-btn delete-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleFileDelete(file)
                    }}
                    title={t('common.delete')}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedFile && (
        <div className="file-preview">
            <div className="preview-header">
              <h4>{t('gallery.previewTitle')}</h4>
            <button 
              className="close-btn"
              onClick={() => setSelectedFile(null)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div className="preview-content">
            {selectedFile.file_type === 'image' && (
              <img 
                src={`/files/preview?filename=${selectedFile.filename}`}
                alt={selectedFile.filename} 
                className="full-preview"
              />
            )}
            {selectedFile.file_type === 'audio' && (
              <audio controls className="full-preview">
                <source src={`http://localhost:8000/files/preview?filename=${selectedFile.filename}`} />
                {t('gallery.browserNotSupportAudio')}
               </audio>
            )}
            {selectedFile.file_type === 'video' && (
              <video controls className="full-preview">
                <source src={`http://localhost:8000/files/preview?filename=${selectedFile.filename}`} />
                {t('gallery.browserNotSupportVideo')}
              </video>
            )}
            {selectedFile.file_type === 'document' && (
              <div className="document-preview">
                <p>{t('gallery.documentPreviewNotAvailable')}</p>
                <button 
                  className="preview-download-btn"
                  onClick={() => handleFileDownload(selectedFile)}
                >
                  {t('gallery.downloadToView')}
                </button>
              </div>
            )}
            {selectedFile.file_type === 'other' && (
              <div className="other-preview">
                <p>{t('gallery.previewNotAvailable')}</p>
                <button 
                  className="preview-download-btn"
                  onClick={() => handleFileDownload(selectedFile)}
                >
                  {t('common.download')}
                </button>
              </div>
            )}
          </div>
          <div className="file-details">
              <h5>{t('gallery.details')}</h5>
              <div className="detail-row">
                <span className="detail-label">{t('gallery.detail.name')}</span>
                <span className="detail-value">{selectedFile.filename}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t('gallery.detail.type')}</span>
                <span className="detail-value">{selectedFile.content_type}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t('gallery.detail.size')}</span>
                <span className="detail-value">{formatFileSize(selectedFile.file_size)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t('gallery.detail.uploaded')}</span>
                <span className="detail-value">{formatDate(selectedFile.upload_time)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t('gallery.detail.path')}</span>
                <span className="detail-value">{selectedFile.relative_path}</span>
              </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Gallery