import React from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../types';
import { getHandleColorByDataType } from '../../utils/handleColorUtils';

interface GenericNodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (newData: WorkflowNode['data']) => void;
  selected?: boolean;
}

const GenericNode: React.FC<GenericNodeProps> = ({ data, onDataChange }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层
  };

  const handleParamChange = (paramName: string, value: any) => {
    if (onDataChange) {
      const updatedParams = {
        ...data.params,
        [paramName]: {
          ...data.params?.[paramName],
          value
        }
      };
      onDataChange({ ...data, params: updatedParams });
    }
  };

  // 计算连接点的最大数量，用于设置CSS变量
  const maxHandleCount = Math.max(data.inputs?.length || 0, data.outputs?.length || 0);

  // 获取参数 - 如果data.params是一个空对象，则使用默认参数（如果有）
  // 这里处理的情况是data.params存在但为空对象的情况
  const params = Object.keys(data.params || {}).length > 0 ? data.params : {
    // 为不同类型的节点添加基本默认参数
    ...(data.type === 'Transform' && {
      mapping: {
        name: 'mapping',
        label: 'Mapping',
        type: 'dict',
        value: '{}'
      },
      transform_type: {
        name: 'transform_type',
        label: 'Transform Type',
        type: 'string',
        value: 'str'
      }
    }),
    ...(data.type === 'DatabaseOutput' && {
      connection: {
        name: 'connection',
        label: 'Connection',
        type: 'dict',
        value: '{}'
      },
      table: {
        name: 'table',
        label: 'Table',
        type: 'string',
        value: ''
      }
    }),
    ...(data.type === 'APIOutput' && {
      url: {
        name: 'url',
        label: 'URL',
        type: 'string',
        value: ''
      },
      method: {
        name: 'method',
        label: 'Method',
        type: 'string',
        value: 'POST'
      },
      headers: {
        name: 'headers',
        label: 'Headers',
        type: 'dict',
        value: '{}'
      }
    })
  };

  return (
    <div className="react-flow__node generic-node" onClick={handleNodeClick} style={{ '--handle-count': maxHandleCount } as React.CSSProperties}>
      {/* 标题区域 */}
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      {/* 连接区域 */}
      <div className="connection-area">
        {/* Input handles with labels */}
        <div className="handles-column left-handles">
          {data.inputs?.map((input: NodeInput, index: number) => (
            <div key={`${input.name}-${index}`} className="handle-item">
              <Handle
                type="target"
                position={Position.Left}
                id={`${input.name}-handle`}
                className="node-handle"
                style={{ 
                  background: getHandleColorByDataType(input.type || ''),
                  left: 0
                }}
              />
              <span className="handle-label">{input.name}</span>
            </div>
          ))}
        </div>
        
        {/* Central content placeholder */}
        <div className="central-content-placeholder"></div>
        
        {/* Output handles with labels */}
        <div className="handles-column right-handles">
          {data.outputs?.map((output: NodeOutput, index: number) => (
            <div key={`${output.name}-${index}`} className="handle-item">
              <Handle
                type="source"
                position={Position.Right}
                id={`${output.name}-handle`}
                className="node-handle"
                style={{ 
                  background: getHandleColorByDataType(output.type || ''),
                  right: 0
                }}
              />
              <span className="handle-label">{output.name}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* 参数控制区域 */}
      <div className="parameter-control-area">
        {Object.entries(params).map(([key, param]) => {
          const typedParam = param as NodeParam;
          return (
            <div key={key} className="param-group">
              <label className="param-label">{typedParam.label}</label>
              <input
                type={typedParam.type === 'number' ? 'number' : 'text'}
                value={typedParam.value as string | number}
                className="node-input"
                onChange={(e) => {
                  const newValue = typedParam.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
                  handleParamChange(key, newValue);
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

// 自定义比较函数，避免不必要的重渲染
const areEqual = (prevProps: GenericNodeProps, nextProps: GenericNodeProps) => {
  // 检查节点是否被选中
  if (prevProps.selected !== nextProps.selected) return false;
  
  // 检查参数值是否变化
  const prevParams = prevProps.data.params || {};
  const nextParams = nextProps.data.params || {};
  const paramKeys = [...new Set([...Object.keys(prevParams), ...Object.keys(nextParams)])];
  
  for (const key of paramKeys) {
    const prevParam = prevParams[key];
    const nextParam = nextParams[key];
    
    // 检查参数是否存在或值是否变化
    if (!prevParam || !nextParam) return false;
    if (prevParam.value !== nextParam.value) return false;
  }
  
  // 所有关键属性都没有变化，不需要重渲染
  return true;
};

export default React.memo(GenericNode as React.FC<GenericNodeProps>, areEqual);