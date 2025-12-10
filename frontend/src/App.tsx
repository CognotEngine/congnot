import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import './App.css'
import './ReactFlowDarkTheme.css'
import NodePalette from './components/NodePalette'
import LivePreview from './components/LivePreview'
import Gallery from './components/Gallery'
import QueueMonitor from './components/QueueMonitor'
import SettingsWindow from './components/SettingsWindow'
import FileMenu from './components/FileMenu'
import ModelsManager from './components/ModelsManager'
import { SaveIcon, ExportIcon, ExecuteIcon, PreviewIcon, GalleryIcon, QueueIcon, NodePaletteIcon, SettingsIcon, MinimizeIcon, MaximizeIcon, CloseIcon, ModelsIcon } from './components/Icons'
import { validateWorkflowData, frontendToBackendWorkflow, workflowDataToFrontendWorkflow } from './utils/dataMapper'
import { getEdgeColorByDataType } from './utils/handleColorUtils'
import { WorkflowData, NodeInput, NodeOutput, NodeData } from './types'
import { useI18n } from './contexts/I18nContext'
import ReactFlow, {
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ConnectionLineType
} from 'reactflow'
import 'reactflow/dist/style.css'

// Import custom node components
import ImageOutputNode from './components/nodes/ImageOutputNode'
import TextOutputNode from './components/nodes/TextOutputNode'
import TextInputNode from './components/nodes/TextInputNode'
import GenericNode from './components/nodes/GenericNode'
import PreviewOutputNodeExample from './components/nodes/PreviewOutputNodeExample'
import ControlNodeExample from './components/nodes/ControlNodeExample'
import StableDiffusionGenerateNode from './components/nodes/StableDiffusionGenerateNode'
import StableDiffusionImageToImageNode from './components/nodes/StableDiffusionImageToImageNode'

// Import input nodes
import ImageInputNode from './components/nodes/inputs/ImageInputNode'
import ClipTextEncodeNode from './components/nodes/inputs/ClipTextEncodeNode'
import LoadCheckpointNode from './components/nodes/inputs/LoadCheckpointNode'

// Import postprocessing nodes
import SaveImageNode from './components/nodes/postprocessing/SaveImageNode'
import ImageManipulationNode from './components/nodes/postprocessing/ImageManipulationNode'
import VAEDecodeNode from './components/nodes/postprocessing/VAEDecodeNode'

// Import processing nodes
import KSamplerNode from './components/nodes/processing/KSamplerNode'

// Import utility nodes
import PreviewNode from './components/nodes/utils/PreviewNode'

// AI video nodes now use GenericNode - imports removed

// Define custom node types inside App component
// NOTE: This application ONLY uses custom nodes. No React Flow built-in nodes are registered or used.

function App() {
  // Electron window instance is handled by the main process
  // Declare appWindow for TypeScript (it should be available from main process in production)
  const appWindow = (window as any)?.appWindow;
  
  // 设置窗口状态
  const [showSettings, setShowSettings] = useState(false);
  const [showQueueMonitor, setShowQueueMonitor] = useState(false);
  const [showModelsManager, setShowModelsManager] = useState(false);
  const { t } = useI18n();
  

  
  useEffect(() => {
    const rootElement = document.getElementById('root');
    if (rootElement) {
      const appElement = rootElement.querySelector('.app');
      if (appElement) {
        // 可以在这里添加其他初始化逻辑
      }
    }
    
    // 点击事件调试已移除
  }, []);
  
  // 添加节点面板显示状态
  const [showNodePalette, setShowNodePalette] = useState(true);
  // 节点列表显示状态已移除（未使用）
  
  const [workflow, setWorkflow] = useState<WorkflowData>({
    nodes: [],
    edges: []
  })
  const [showPreview, setShowPreview] = useState(false)
  const [showGallery, setShowGallery] = useState(false)
  
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionProgress, setExecutionProgress] = useState(0)
  const [executionStatus, setExecutionStatus] = useState('')
  const [executionId, setExecutionId] = useState<string | null>(null)
  const [executionResults, setExecutionResults] = useState<any | null>(null)
  
  const handleSaveWorkflow = async () => {
    // 先更新workflow数据
    setWorkflow((wf) => ({
      ...wf,
      nodes: nodes,
      edges: edges,
    }));
    
    // 使用最新的workflow数据
    const workflowData = { ...workflow, nodes: nodes, edges: edges };
    
    if (workflowData.nodes.length > 0 || workflowData.edges.length > 0) {
      const workflowId = `workflow_${Date.now()}`;
      const workflowName = prompt('Please enter workflow name:', 'My Workflow');
      
      if (workflowName) {
        try {
          const response = await fetch('http://127.0.0.1:8000/workflows', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              id: workflowId,
              name: workflowName,
              data: workflowData,
              createdAt: new Date().toISOString()
            }),
          });
          
          if (response.ok) {
            await response.json();
            
            // 更新本地存储
            const workflows = JSON.parse(localStorage.getItem('savedWorkflows') || '[]');
            workflows.push({
              id: workflowId,
              name: workflowName,
              data: workflowData,
              createdAt: new Date().toISOString()
            });
            localStorage.setItem('savedWorkflows', JSON.stringify(workflows));
            
            alert('Workflow saved successfully!');
          } else {
            const errorData = await response.json().catch(() => ({}));
            alert(`Failed to save workflow to server: ${errorData.detail || response.statusText}`);
          }
        } catch (error: unknown) {
            console.error('Error saving workflow:', error);
            alert(`Error saving workflow: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }
    } else {
      alert('No workflow to save');
    }
  };

  const handlePreviewToggle = () => {
    setShowPreview(!showPreview)
    if (showGallery) {
      setShowGallery(false)
    }
  }

  const handleGalleryToggle = () => {
    setShowGallery(!showGallery)
    if (showPreview) {
      setShowPreview(false)
    }
    if (showQueueMonitor) {
      setShowQueueMonitor(false)
    }
  }

  const handleQueueMonitorToggle = () => {
    setShowQueueMonitor(!showQueueMonitor)
    if (showPreview) {
      setShowPreview(false)
    }
    if (showGallery) {
      setShowGallery(false)
    }
  }
  
  useEffect(() => {
    let intervalId: number | null = null
    
    if (isExecuting && executionId) {
      intervalId = window.setInterval(async () => {
        try {
          const response = await fetch(`/execution/status?executionId=${executionId}`)
          if (response.ok) {
            const data = await response.json()
            console.log('Execution Status:', data)
            
            setExecutionStatus(data.status)
            
            if (data.results && data.results.node_count) {
              const completedNodes = Object.keys(data.results).filter(key => key !== 'node_count').length
              const progress = Math.min(100, Math.floor((completedNodes / data.results.node_count) * 100))
              setExecutionProgress(progress)
            }
            
            if (data.status === 'completed' || data.status === 'error') {
              if (intervalId) {
                clearInterval(intervalId)
              }
              setIsExecuting(false)
              
              if (data.status === 'completed') {
                setExecutionResults(data.results)
                alert('Workflow Executed Successfully!')
              } else if (data.status === 'error') {
                alert('Error Executing Workflow: ' + data.error)
              }
            }
          }
        } catch (error: unknown) {
          console.error('Error fetching execution status:', error)
          if (intervalId) {
            clearInterval(intervalId)
          }
          setIsExecuting(false)
        }
      }, 500)
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [isExecuting, executionId])

  // ReactFlow相关状态
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const reactFlowInstance = useReactFlow()
  
  // 处理拖拽放置事件
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])
  
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect()
      // Get drag data in application/reactflow format
      const data = event.dataTransfer.getData('application/reactflow')

      if (data && reactFlowBounds && reactFlowInstance) {
        const node = JSON.parse(data)
        const position = reactFlowInstance.screenToFlowPosition({
          x: event.clientX - reactFlowBounds.left,
          y: event.clientY - reactFlowBounds.top,
        })

        const newNode = {
          ...node,
          position,
        }

        // 直接更新nodes和workflow，避免循环更新
        setNodes((nds) => nds.concat(newNode))
        setWorkflow((wf) => ({
          ...wf,
          nodes: [...wf.nodes, newNode],
        }))
      }
    },
    [reactFlowInstance, setNodes, setWorkflow]
  )

  // 处理节点连接
  const onConnect = useCallback(
    (params: any) => {
      // 查找源节点和目标节点以获取数据类型信息
      const sourceNode = nodes.find(node => node.id === params.source);
      const targetNode = nodes.find(node => node.id === params.target);
      
      // 获取源输出和目标输入的数据类型
      let sourceDataType = '';
      if (sourceNode && params.sourceHandle) {
        const output = sourceNode.data.outputs?.find((out: NodeOutput) => out.name === params.sourceHandle);
        sourceDataType = output?.type || '';
      }
      
      let targetDataType = '';
      if (targetNode && params.targetHandle) {
        const input = targetNode.data.inputs?.find((inp: NodeInput) => inp.name === params.targetHandle);
        targetDataType = input?.type || '';
      }
      
      // 数据类型兼容性检查：只有相同数据类型才能连接（或其中一个为空时）
      if (sourceDataType && targetDataType && sourceDataType !== targetDataType) {
        // 数据类型不兼容，阻止连接
        console.log(`连接失败：数据类型不兼容 ${sourceDataType} -> ${targetDataType}`);
        return;
      }
      
      // 确定连接线的数据类型（优先使用源节点的数据类型）
      const dataType = sourceDataType || targetDataType || 'default';
      
      // 创建新的边配置
      const newEdgeParams = {
        ...params,
        type: dataType || 'default', // 使用数据类型作为边缘类型
        data: {
          ...params.data,
          dataType // 添加数据类型信息
        },
        style: {
          ...params.style,
          strokeWidth: 2,
          stroke: getEdgeColorByDataType(dataType) // 根据数据类型设置颜色
        }
      };
      
      setEdges((eds) => addEdge(newEdgeParams, eds));
    },
    [setEdges, nodes]
  );

  // 节点变化时更新workflow - 但不监听nodes变化以避免循环
  // 处理节点数据变化
  const handleNodeDataChange = useCallback((nodeId: string, updatedData: Partial<NodeData>) => {
    setNodes((nds) => {
      const updatedNodes = nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...updatedData } } : node
      );
      // 同时更新workflow数据
      setWorkflow((wf) => ({
        ...wf,
        nodes: updatedNodes,
        edges: wf.edges,
      }));
      return updatedNodes;
    });
  }, [setNodes, setWorkflow]);

  // Register custom node types for dark theme with onDataChange injected
  // Helper function to wrap a node component with onDataChange
  const withOnDataChange = useCallback((Component: React.ComponentType<any>) => {
    return (props: any) => <Component {...props} onDataChange={handleNodeDataChange} />;
  }, [handleNodeDataChange]);

  // NOTE: This application ONLY uses custom nodes. No React Flow built-in nodes are registered or used.
  const nodeTypes = useMemo(() => {
    return {
      // AI Image Processing Nodes
      imageOutput: withOnDataChange(ImageOutputNode),
      stable_diffusion_generate: withOnDataChange(StableDiffusionGenerateNode),
      stable_diffusion_image_to_image: withOnDataChange(StableDiffusionImageToImageNode),
      imageInput: withOnDataChange(ImageInputNode),
      imageManipulation: withOnDataChange(ImageManipulationNode),
      saveImage: withOnDataChange(SaveImageNode),
      vaeDecode: withOnDataChange(VAEDecodeNode),
      previewNode: withOnDataChange(PreviewNode),
      
      // AI Generator Nodes
      ClipTextEncode: withOnDataChange(ClipTextEncodeNode),
      CheckpointLoaderSimple: withOnDataChange(LoadCheckpointNode),
      KSampler: withOnDataChange(KSamplerNode),
      
      // AI Video Processing Nodes now use GenericNode
      videoLoad: withOnDataChange(GenericNode),
      frameIndexManager: withOnDataChange(GenericNode),
      opticalFlowCalculator: withOnDataChange(GenericNode),
      frameProcessorLoop: withOnDataChange(GenericNode),
      fusionImage: withOnDataChange(GenericNode),
      videoComposer: withOnDataChange(GenericNode),
      promptInterpolator: withOnDataChange(GenericNode),
      
      // Text Nodes
      TextInput: withOnDataChange(TextInputNode),
      TextOutput: withOnDataChange(TextOutputNode),
      
      // Missing node types using GenericNode
      FileInput: withOnDataChange(GenericNode),
      APIInput: withOnDataChange(GenericNode),
      DatabaseInput: withOnDataChange(GenericNode),
      TextProcessing: withOnDataChange(GenericNode),
      MathOperation: withOnDataChange(GenericNode),
      Filter: withOnDataChange(GenericNode),
      // Additional missing node types from node-config.json
      Loop: withOnDataChange(GenericNode),
      processing: withOnDataChange(GenericNode),
      AddNumbers: withOnDataChange(GenericNode),
      MultiplyNumbers: withOnDataChange(GenericNode),
      CompareNumbers: withOnDataChange(GenericNode),
      ConcatenateStrings: withOnDataChange(GenericNode),
      Branch: withOnDataChange(GenericNode),
      Sampler: withOnDataChange(GenericNode),
      BaseConfigExample: withOnDataChange(GenericNode),
      DatabaseOutput: withOnDataChange(GenericNode),
      APIOutput: withOnDataChange(GenericNode),
      FileOutput: withOnDataChange(GenericNode),
      AIProcessing: withOnDataChange(GenericNode),
      Transform: withOnDataChange(GenericNode),
      
      // Default fallback
      default: withOnDataChange(GenericNode),
      
      // Example Nodes
      PreviewOutputExample: withOnDataChange(PreviewOutputNodeExample),
      ControlNodeExample: withOnDataChange(ControlNodeExample)
    };
  }, [withOnDataChange]);

  // 仅在初始加载时从workflow加载节点和边
  useEffect(() => {
    if (workflow.nodes && workflow.edges && workflow.nodes.length > 0) {
      setNodes(workflow.nodes)
      setEdges(workflow.edges)
    }
  }, []) // 空依赖数组，只运行一次



  return (
    <div className="app">
      {/* 移除调试按钮 */}
      <div className="app-header">
        <h1>Cognot</h1>
        
        <div className="app-text-options">
          <FileMenu nodes={nodes} edges={edges} setNodes={setNodes} setEdges={setEdges} />
          <button 
            type="button" 
            className="text-option-btn"
            onClick={() => console.log('Help clicked')}
          >
            {t('common.help')}
          </button>
        </div>
        
        {isExecuting && (
          <div className="execution-progress-container">
            <div className="app-progress">
              <progress value={executionProgress} max="100" className="progress-bar" />
              <span className="progress-status">
                {executionStatus.charAt(0).toUpperCase() + executionStatus.slice(1)} ({executionProgress}%)
              </span>
            </div>
          </div>
        )}
        
        <div className="app-controls">
          <button type="button" 
            className="icon-btn"
            title={t('common.saveWorkflow')}
            onClick={handleSaveWorkflow}
          >
            <SaveIcon />
          </button>
          <button 
            type="button" 
            className="icon-btn"
            title={t('common.exportWorkflow')}
            onClick={() => {
              const frontendWorkflow = workflowDataToFrontendWorkflow(workflow)
              const validation = validateWorkflowData(frontendWorkflow)
              if (validation.isValid) {
                const backendWorkflow = frontendToBackendWorkflow(frontendWorkflow)
                console.log('Export Workflow (Backend Format):', backendWorkflow)
                
                const dataStr = JSON.stringify(backendWorkflow, null, 2)
                const dataBlob = new Blob([dataStr], { type: 'application/json' })
                const url = URL.createObjectURL(dataBlob)
                const link = document.createElement('a')
                link.href = url
                link.download = 'workflow.json'
                link.click()
                URL.revokeObjectURL(url)
              } else {
                console.error(t('common.workflowValidationFailed'), validation.errors)
                alert(t('common.workflowValidationFailed') + ' ' + validation.errors.join(', '))
              }
            }}
          >
            <ExportIcon />
          </button>
          <button type="button" 
            className="icon-btn"
            title={t('common.executeWorkflow')}
            onClick={() => {
              const frontendWorkflow = workflowDataToFrontendWorkflow(workflow)
              const validation = validateWorkflowData(frontendWorkflow)
              if (validation.isValid) {
                setIsExecuting(true)
                setExecutionProgress(0)
                setExecutionStatus('submitting')
                setExecutionId(null)
                
                const backendWorkflow = frontendToBackendWorkflow(frontendWorkflow)
                console.log('Execute Workflow (Backend Format):', backendWorkflow)
                
                fetch('/execution/execute', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json'
                  },
                  body: JSON.stringify(backendWorkflow)
                })
                .then(response => {
                  if (response.ok) {
                    return response.json()
                  } else {
                    throw new Error('Failed to Execute Workflow')
                  }
                })
                .then(data => {
                  console.log('Execution Started:', data)
                  setExecutionId(data.execution_id)
                  setExecutionStatus('pending')
                })
                .catch(error => {
                  console.error('Workflow Execution Error:', error)
                  alert('Error Executing Workflow: ' + error.message)
                  setIsExecuting(false)
                })
              } else {
                console.error('Workflow Validation Failed:', validation.errors)
                alert('Workflow Validation Failed: ' + validation.errors.join(', '))
              }
            }}
          >
            <ExecuteIcon />
          </button>
          <button 
            type="button" 
            className={`icon-btn preview-btn ${showPreview ? 'active' : ''}`} 
            title={t('common.livePreview')}
            onClick={handlePreviewToggle}
          >
            <PreviewIcon />
          </button>
          <button type="button"
            className={`icon-btn gallery-btn ${showGallery ? 'active' : ''}`}
            title={t('common.resource')}
            onClick={handleGalleryToggle}
          >
            <GalleryIcon />
          </button>
          <button
            type="button"
            className={`icon-btn queue-btn ${showQueueMonitor ? 'active' : ''}`}
            title={t('common.queueMonitor')}
            onClick={handleQueueMonitorToggle}
          >
            <QueueIcon />
          </button>
          {/* 窗口控制按钮分隔符 */}
          <div className="window-controls-separator"></div>
          
          {/* 窗口控制按钮 */}
          <button type="button"
            className="icon-btn"
            onClick={async () => {
              try {
                if (appWindow) {
                  await appWindow.minimize();
                } else {
                  // Browser fallback
                  window.resizeTo(window.outerWidth, 300);
                }
              } catch (error) {
                console.error('Failed to minimize window:', error);
                // Browser fallback
                window.resizeTo(window.outerWidth, 300);
              }
            }}
          >
            <MinimizeIcon />
          </button>
          <button
            type="button"
            className="icon-btn"
            onClick={async () => {
              try {
                if (appWindow) {
                  const isMax = await appWindow.isMaximized();
                  if (isMax) {
                    await appWindow.unmaximize();
                  } else {
                    await appWindow.maximize();
                  }
                }
              } catch (error) {
                console.error('Failed to toggle window maximize:', error);
              }
            }}
          >
            <MaximizeIcon />
          </button>
          <button type="button"
            className="icon-btn close-btn"
            onClick={async () => {
              try {
                if (appWindow) {
                  await appWindow.close();
                } else {
                  // Browser fallback
                  window.close();
                }
              } catch (error) {
                console.error('Failed to close window:', error);
                // Browser fallback
                window.close();
              }
            }}
          >
            <CloseIcon />
          </button>
        </div>
      </div>
      <div className="app-main">
        <div className="sidebar narrow-nav">
          <button type="button" 
            className={`nav-btn ${showNodePalette ? 'active' : ''}`}
            title={t('narrowNav.nodePalette')}
            onClick={() => setShowNodePalette(!showNodePalette)}
          >
            <NodePaletteIcon size={24} />
          </button>
          
          <button type="button" 
            className={`nav-btn ${showModelsManager ? 'active' : ''}`}
            title={t('narrowNav.models')}
            onClick={() => setShowModelsManager(!showModelsManager)}
          >
            <ModelsIcon size={24} />
          </button>
         

          
          {/* 空的div用于将设置按钮推到最下面 */}
          <div style={{ flex: 1 }}></div>
          <button type="button" 
            className="nav-btn"
            title={t('narrowNav.settings')}
            onClick={() => setShowSettings(true)}
          >
            <SettingsIcon size={24} />
          </button>
        </div>
        <div className="left-panels-container">
          <div className={`sidebar left-sidebar ${showNodePalette ? 'expanded' : 'collapsed'}`}>
            <NodePalette setNodes={setNodes} setEdges={setEdges} />
          </div>
          {showModelsManager && (
            <aside className="sidebar left-sidebar models-manager-panel">
              <ModelsManager />
            </aside>
          )}
        </div>
        <div className="app-content" ref={reactFlowWrapper}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onInit={() => {}}
              onDragOver={onDragOver}
              onDrop={onDrop}
              fitView
              nodeTypes={nodeTypes}
              // 性能优化配置
              preventScrolling={true}
              panOnScroll={false}
              panOnDrag={true}
              zoomOnDoubleClick={true}
              zoomOnScroll={true}
              // 边缘选择默认启用，无需额外配置
              // Connection line styling
              connectionLineStyle={{
                stroke: '#4caf50',
                strokeWidth: 2,
                strokeDasharray: '5 5'
              }}
              connectionLineType={ConnectionLineType.SmoothStep}
            >
              <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
              <Controls />
              <MiniMap
                nodeColor={(node) => (node.type === 'input' ? '#0041d0' : '#ff0072')}
                nodeStrokeWidth={3}
                zoomable
                pannable
              />
            </ReactFlow>
        </div>

        {showPreview && (
          <aside className="sidebar preview-sidebar">
            <LivePreview executionResults={executionResults || undefined} isRunning={isExecuting} />
          </aside>
        )}
        {showGallery && (
          <aside className="sidebar gallery-sidebar">
            <Gallery />
          </aside>
        )}
        {showQueueMonitor && (
          <aside className="sidebar queue-sidebar">
            <QueueMonitor />
          </aside>
        )}

      </div>
      
      {/* 设置窗口 */}
      <SettingsWindow 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </div>
  )
}

export default App
