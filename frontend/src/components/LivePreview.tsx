import { useState, useEffect, useRef } from 'react'
import { useI18n } from '../contexts/I18nContext'
import './LivePreview.css'

interface LogEntry {
  timestamp: number;
  level?: 'debug' | 'info' | 'warn' | 'error';
  message: string;
}

interface TimelineEvent {
  timestamp: number;
  nodeId: string;
  nodeName: string;
  status: 'started' | 'completed' | 'error';
  duration?: number;
}

interface ExecutionResult {
  [nodeId: string]: any;
  logs?: LogEntry[];
  timeline?: TimelineEvent[];
}

interface LivePreviewProps {
  workflow?: any;
  isRunning: boolean;
  executionResults?: ExecutionResult;
}

interface PreviewContent {
  image?: string;
  html?: string;
  [key: string]: any;
}

const LivePreview = ({ workflow, isRunning, executionResults }: LivePreviewProps) => {
  const { t } = useI18n()
  const [previewContent, setPreviewContent] = useState<PreviewContent | string | null>(null)
  const [activeTab, setActiveTab] = useState<'output' | 'logs' | 'timeline'>('output') 
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const logsEndRef = useRef<HTMLDivElement>(null)

  
  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [logs])

  
  useEffect(() => {
    if (executionResults) {
      
      
      if (typeof executionResults === 'object' && executionResults !== null) {
        
        const formattedResults: Record<string, any> = {};
        
        
        const hasExpectedNodes = Object.keys(executionResults).some(key => 
          key.startsWith('node_') || key.includes('input-') || key.includes('output-')
        );
        
        if (hasExpectedNodes) {
          
          Object.entries(executionResults).forEach(([nodeId, result]) => {
            formattedResults[nodeId] = result;
          });
        } else {
          
          let nodeCount = 1;
          Object.entries(executionResults).forEach(([_, result]) => {
            const newNodeId = `node_${nodeCount}`;
            formattedResults[newNodeId] = result;
            nodeCount++;
          });
        }
        
        
        if (Object.keys(formattedResults).length === 1) {
          const firstNodeId = Object.keys(formattedResults)[0];
          const firstNodeResult = formattedResults[firstNodeId];
          
          if (firstNodeResult.value) {
            setPreviewContent(firstNodeResult.value);
          } else if (firstNodeResult.result) {
            setPreviewContent(firstNodeResult.result);
          } else {
            setPreviewContent(firstNodeResult);
          }
        } else {
          
          setPreviewContent(formattedResults);
        }
      } else {
        
        setPreviewContent(executionResults as string);
      }
      
      
      if (executionResults.logs) {
        setLogs(prev => [...prev, ...(executionResults.logs || [])])
      }
      
      
      if (executionResults.timeline) {
        setTimeline(prev => [...prev, ...(executionResults.timeline || [])])
      }
    }
  }, [executionResults])

  
  const formatLogTime = (timestamp: number): string => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString()
  }

  
  const renderOutput = () => {
    if (!previewContent) {
      return (
        <div className="preview-placeholder">
          <p>{t('livePreview.placeholder.main')}</p>
          <p className="hint">{t('livePreview.placeholder.hint')}</p>
        </div>
      )
    }

    
    if (typeof previewContent === 'string') {
      return <div className="preview-text">{previewContent}</div>
    } else if ('image' in previewContent && previewContent.image) {
      return <img src={previewContent.image} alt="Workflow output" className="preview-image" />;
    } else if ('html' in previewContent && previewContent.html) {
      return <div dangerouslySetInnerHTML={{ __html: previewContent.html }} className="preview-html" />;
    } else {
      return (
        <div className="preview-json">
          <pre>{JSON.stringify(previewContent, null, 2)}</pre>
        </div>
      )
    }
  }

  
  const renderLogs = () => {
    if (logs.length === 0) {
      return <div className="logs-placeholder">{t('livePreview.placeholder.noLogs')}</div>
    }

    return (
      <div className="logs-container">
        {logs.map((log, index) => (
          <div key={index} className={`log-entry log-${log.level || 'info'}`}>
            <span className="log-time">{formatLogTime(log.timestamp)}</span>
            <span className="log-level">[{log.level || 'INFO'}]</span>
            <span className="log-message">{log.message}</span>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    )
  }

  
  const renderTimeline = () => {
    if (timeline.length === 0) {
      return <div className="timeline-placeholder">{t('livePreview.placeholder.noTimeline')}</div>
    }

    return (
      <div className="timeline-container">
        {timeline.map((event, index) => (
          <div key={index} className="timeline-event">
            <div className="timeline-time">{formatLogTime(event.timestamp)}</div>
            <div className="timeline-content">
              <div className="timeline-title">{event.nodeName} ({event.nodeId})</div>
              <div className={`timeline-status status-${event.status}`}>{event.status}</div>
              {event.duration && (
                <div className="timeline-duration">{event.duration}ms</div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="live-preview-container">
      <div className="live-preview-header">
        <h3>{t('livePreview.title')}</h3>
        <div className="preview-controls">
          <button 
            className={`control-btn ${isRunning ? 'running' : ''}`}
            disabled={!workflow || workflow.nodes.length === 0}
          >
            {isRunning ? 
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> {t('livePreview.pause')}</> : 
              <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg> {t('livePreview.run')}</>}
          </button>
          <button className="button" onClick={() => {
            setLogs([]);
            setTimeline([]);
            setPreviewContent(null);
          }}>
            <svg className="svgIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg> {t('livePreview.clear')}
          </button>
        </div>
      </div>
      
      <div className="preview-tabs">
        <button 
          className={`tab-btn ${activeTab === 'output' ? 'active' : ''}`}
          onClick={() => setActiveTab('output')}
        >
          {t('livePreview.tabs.output')}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          {t('livePreview.tabs.logs')}
          {logs.length > 0 && <span className="tab-badge">{logs.length}</span>}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          {t('livePreview.tabs.timeline')}
        </button>
      </div>
      
      <div className="preview-content">
        {activeTab === 'output' && renderOutput()}
        {activeTab === 'logs' && renderLogs()}
        {activeTab === 'timeline' && renderTimeline()}
      </div>
    </div>
  )
}

export default LivePreview