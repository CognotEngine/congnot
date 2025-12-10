import React, { useState, useRef, useEffect } from 'react';
import { frontendToBackendWorkflow, backendToFrontendWorkflow, validateWorkflowData, BackendWorkflow, frontendWorkflowToWorkflowData, workflowDataToFrontendWorkflow } from '../utils/dataMapper';
import { WorkflowData, WorkflowNode, WorkflowEdge } from '../types';
import { t } from '../utils/i18n';

interface FileMenuProps {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  setNodes: (nodes: WorkflowNode[] | ((nodes: WorkflowNode[]) => WorkflowNode[])) => void;
  setEdges: (edges: WorkflowEdge[] | ((edges: WorkflowEdge[]) => WorkflowEdge[])) => void;
}

const FileMenu: React.FC<FileMenuProps> = ({ nodes, edges, setNodes, setEdges }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const fileMenuRef = useRef<HTMLDivElement>(null);

  // 点击外部区域关闭菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (fileMenuRef.current && !fileMenuRef.current.contains(event.target as Element)) {
        setMenuOpen(false);
      }
    };

    // 添加事件监听器
    document.addEventListener('mousedown', handleClickOutside);
    
    // 清理函数
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSaveToPreset = () => {
    console.log('Save to preset');
    // 这里可以实现保存到预设的功能
    setMenuOpen(false);
  };

  const handleDownload = () => {
    console.log('Download workflow');
    // Convert ReactFlow nodes and edges to WorkflowData first
    const workflowData: WorkflowData = { nodes, edges };
    // Then convert WorkflowData to FrontendWorkflow format expected by the validation and conversion functions
    const frontendWorkflow = workflowDataToFrontendWorkflow(workflowData);
    
    const validation = validateWorkflowData(frontendWorkflow);
    if (validation.isValid) {
      const backendWorkflow = frontendToBackendWorkflow(frontendWorkflow);
      const dataStr = JSON.stringify(backendWorkflow, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'workflow.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else {
      console.error('Workflow Validation Failed:', validation.errors);
      alert('Workflow Validation Failed: ' + validation.errors.join(', '));
    }
    setMenuOpen(false);
  };

  const handleImport = () => {
    console.log('Import workflow');
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const importedData = JSON.parse(event.target?.result as string);
            console.log('Imported data:', importedData);
            
            // 检查导入的数据格式
            let workflowToSet: WorkflowData;
            
            // 如果是后端格式的工作流，转换为前端格式
            if (importedData.nodes && importedData.edges) {
              // 检查节点是否有position属性（前端格式）
              if (importedData.nodes[0]?.position) {
                // 已经是前端格式，直接转换为WorkflowData
                workflowToSet = {
                  nodes: importedData.nodes || [],
                  edges: importedData.edges || []
                };
              } else {
                // 后端格式，需要转换
                const frontendWorkflow = backendToFrontendWorkflow(importedData as BackendWorkflow);
                if (frontendWorkflow) {
                  // 使用转换函数将FrontendWorkflow转换为WorkflowData
                  workflowToSet = frontendWorkflowToWorkflowData(frontendWorkflow);
                } else {
                  throw new Error('Failed to convert backend workflow to frontend format');
                }
              }
            } else if (importedData.data?.nodes && importedData.data?.edges) {
              // 可能是外部格式，需要转换
              // 这里简单处理，将数据直接作为工作流
              workflowToSet = {
                nodes: importedData.data.nodes || [],
                edges: importedData.data.edges || []
              };
            } else if (importedData.workflow && importedData.workflow.nodes && importedData.workflow.edges) {
              // 是带有workflow字段的格式
              workflowToSet = {
                nodes: importedData.workflow.nodes || [],
                edges: importedData.workflow.edges || []
              };
            } else {
              // 尝试直接使用导入的数据作为工作流
              workflowToSet = {
                nodes: importedData.nodes || [],
                edges: importedData.edges || []
              };
            }
            
            // 设置工作流
            setNodes(workflowToSet.nodes);
            setEdges(workflowToSet.edges);
            alert(t('common.workflowImported'));
          } catch (error) {
            console.error('Error importing workflow:', error);
            alert(`${t('common.errorImportingWorkflow')} ${error instanceof Error ? error.message : String(error)}`);
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
    setMenuOpen(false);
  };

  return (
    <div className="file-menu-container" ref={fileMenuRef}>
      <button
        type="button"
        className="text-option-btn"
        onClick={() => setMenuOpen(!menuOpen)}
      >
        {t('common.file')}
      </button>
      {menuOpen && (
        <div className="file-menu-dropdown">
          <div className="menu-item" onClick={handleSaveToPreset}>
            {t('common.save')}
          </div>
          <div className="menu-item" onClick={handleDownload}>
            {t('common.download')}
          </div>
          <div className="menu-item" onClick={handleImport}>
            {t('common.import')}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileMenu;
