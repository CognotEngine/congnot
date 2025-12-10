import React, { useState, useEffect } from 'react';
import { useI18n } from '../contexts/I18nContext';
import './QueueMonitor.css';

interface QueueInfo {
  queued: number;
  started: number;
  finished: number;
  failed: number;
}

interface Task {
  id: string;
  status: string;
  created_at: string;
  started_at?: string;
  ended_at?: string;
}

const QueueMonitor: React.FC = () => {
  // 使用i18n上下文
  const { t } = useI18n();
  const [queueInfo, setQueueInfo] = useState<QueueInfo>({
    queued: 0,
    started: 0,
    finished: 0,
    failed: 0
  });
  const [tasks, setTasks] = useState<Task[]>([]);

  const [refreshInterval, setRefreshInterval] = useState<number>(5000);

  // Fetch queue information
  const fetchQueueInfo = async () => {
    try {
    const response = await fetch('/queue/info');
      if (response.ok) {
        const data = await response.json();
        // Extract queue info from the response
        setQueueInfo(data.queue_info);
      }
    } catch (error) {
      console.error('Failed to fetch queue info:', error);
    }
  };

  // Fetch tasks from the actual API endpoint
  const fetchTasks = async () => {
    try {
      const response = await fetch('/queue/tasks');
      if (response.ok) {
        const data = await response.json();
        // Combine all task types into a single list and sort by created_at (newest first)
        const allTasks: Task[] = [
          ...(data.queue_tasks.queued || []),
          ...(data.queue_tasks.started || []),
          ...(data.queue_tasks.finished || []),
          ...(data.queue_tasks.failed || [])
        ].map(task => ({
          id: task.job_id,
          status: task.status,
          created_at: task.created_at,
          started_at: task.started_at,
          ended_at: task.ended_at
        }));
        
        // Sort by created_at (newest first)
        allTasks.sort((a, b) => {
          if (!a.created_at) return 1;
          if (!b.created_at) return -1;
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        });
        
        setTasks(allTasks);
      }
    } catch (error) {
      console.error('Failed to fetch queue tasks:', error);
    }
  };

  // Fetch data initially and set up auto-refresh
  useEffect(() => {
    fetchQueueInfo();
    fetchTasks();

    const interval = setInterval(() => {
      fetchQueueInfo();
      fetchTasks();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString();
  };

  // Get status color class
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'status-queued';
      case 'started':
        return 'status-started';
      case 'finished':
        return 'status-finished';
      case 'failed':
        return 'status-failed';
      default:
        return '';
    }
  };

  // Get translated status text
  const getTranslatedStatus = (status: string) => {
    switch (status) {
      case 'queued':
        return t('queueMonitor.status.queued');
      case 'started':
        return t('queueMonitor.status.started');
      case 'finished':
        return t('queueMonitor.status.finished');
      case 'failed':
        return t('queueMonitor.status.failed');
      default:
        return status;
    }
  };

  return (
    <div className="queue-monitor-container">
      <div className="queue-monitor-header">
        <h2>{t('queueMonitor.title')}</h2>
        <div className="refresh-controls">
          <label htmlFor="refresh-interval">{t('queueMonitor.refresh')}</label>
          <select
            id="refresh-interval"
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
          >
            <option value={1000}>{t('queueMonitor.refresh.1s')}</option>
            <option value={5000}>{t('queueMonitor.refresh.5s')}</option>
            <option value={10000}>{t('queueMonitor.refresh.10s')}</option>
            <option value={30000}>{t('queueMonitor.refresh.30s')}</option>
          </select>
        </div>
      </div>

      {/* Queue Statistics */}
      <div className="queue-stats">
        <div className="stat-card">
          <div className="stat-title">{t('queueMonitor.stats.queued')}</div>
          <div className="stat-value queued">{queueInfo.queued}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">{t('queueMonitor.stats.running')}</div>
          <div className="stat-value started">{queueInfo.started}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">{t('queueMonitor.stats.finished')}</div>
          <div className="stat-value finished">{queueInfo.finished}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">{t('queueMonitor.stats.failed')}</div>
          <div className="stat-value failed">{queueInfo.failed}</div>
        </div>
      </div>

      {/* Tasks Table */}
      <div className="tasks-table-container">
        <h3>{t('queueMonitor.tasks.recent')}</h3>
        <table className="tasks-table">
          <thead>
            <tr>
              <th>{t('queueMonitor.tasks.id')}</th>
              <th>{t('queueMonitor.tasks.status')}</th>
              <th>{t('queueMonitor.tasks.created')}</th>
              <th>{t('queueMonitor.tasks.started')}</th>
              <th>{t('queueMonitor.tasks.ended')}</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id}>
                <td className="task-id">{task.id}</td>
                <td>
                  <span className={`status-badge ${getStatusColor(task.status)}`}>
                    {getTranslatedStatus(task.status)}
                  </span>
                </td>
                <td>{formatDate(task.created_at)}</td>
                <td>{task.started_at ? formatDate(task.started_at) : '-'}</td>
                <td>{task.ended_at ? formatDate(task.ended_at) : '-'}</td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr>
                <td colSpan={5} className="no-tasks">{t('queueMonitor.tasks.noTasks')}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default QueueMonitor;
