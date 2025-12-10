# 节点样式统一指南

## 目标
确保所有新增节点都使用与Stable Diffusion Generate节点相同的外观，保持整个工作流界面的一致性。

## 外观特点
Stable Diffusion Generate节点的外观特点包括：
- 集中式连接点布局（所有连接点集中在节点左侧和右侧）
- 统一的参数组布局（每个参数包含标签和输入框）
- 相同的背景色和边框样式
- 统一的节点头部样式
- 一致的选中状态样式

## 实现方法

### 1. 使用通用节点样式
所有节点都应使用`generic-node`类名，而不是自定义类名：

```jsx
<div className={`react-flow__node generic-node ${selected ? 'selected' : ''}`} onClick={handleNodeClick}>
  {/* 节点内容 */}
</div>
```

### 2. 导入必要的工具函数
确保导入集中式连接点布局函数：

```jsx
import { getConcentratedHandlePosition } from '../../utils/handlePositionUtils';
```

### 3. 使用集中式连接点布局
为所有输入和输出连接点使用集中式布局：

```jsx
{/* Input handles - Concentrated layout */}
data.inputs?.map((input: NodeInput, index: number) => {
  const handleKey = input.id || input.name || `input-${index}`;
  const handleId = input.id || input.name || `input-${index}`;
  
  return (
    <Handle
      key={handleKey}
      type="target"
      position={Position.Left}
      id={`${handleId}-handle`}
      className="input-handle"
      style={getConcentratedHandlePosition(data.inputs, index)}
    />
  );
})

{/* Output handles - Concentrated layout */}
data.outputs?.map((output: NodeOutput, index: number) => {
  const handleKey = output.id || output.name || `output-${index}`;
  const handleId = output.id || output.name || `output-${index}`;
  
  return (
    <Handle
      key={handleKey}
      type="source"
      position={Position.Right}
      id={`${handleId}-handle`}
      className="output-handle"
      style={getConcentratedHandlePosition(data.outputs, index)}
    />
  );
})
```

### 4. 参数组布局
使用统一的参数组布局：

```jsx
<div key={paramName} className="param-group">
  <label className="param-label">{param.label}</label>
  <input
    type={param.type === 'number' ? 'number' : 'text'}
    value={param.value}
    className="node-input"
    onChange={handleChange}
  />
</div>
```

### 5. 导入通用样式文件
确保导入通用样式文件：

```jsx
import './GenericNode.css';
```

## 示例节点结构

```jsx
import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput, NodeParam } from '../../types';
import { getConcentratedHandlePosition } from '../../utils/handlePositionUtils';
import './GenericNode.css';

interface MyNewNodeProps extends NodeProps {
  data: WorkflowNode['data'];
  onDataChange?: (nodeId: string, data: WorkflowNode['data']) => void;
}

const MyNewNode: React.FC<MyNewNodeProps> = ({ id, data, selected, onDataChange }) => {
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
      
      onDataChange(id, { ...data, params: updatedParams });
    }
  };

  return (
    <div className={`react-flow__node generic-node ${selected ? 'selected' : ''}`} onClick={handleNodeClick}>
      {/* Input handles - Concentrated layout */}
      {data.inputs?.map((input: NodeInput, index: number) => {
        const handleKey = input.id || input.name || `input-${index}`;
        const handleId = input.id || input.name || `input-${index}`;
        
        return (
          <Handle
            key={handleKey}
            type="target"
            position={Position.Left}
            id={`${handleId}-handle`}
            className="input-handle"
            style={getConcentratedHandlePosition(data.inputs, index)}
          />
        );
      })}
      
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      <div className="node-content">
        {/* 参数组布局 */}
        {data.params && Object.entries(data.params).map(([key, param]) => {
          const typedParam = param as NodeParam;
          return (
            <div key={key} className="param-group">
              <label className="param-label">{typedParam.label}</label>
              <input
                type={typedParam.type === 'number' ? 'number' : 'text'}
                value={typedParam.value}
                className="node-input"
                onChange={(e) => {
                  handleParamChange(key, typedParam.type === 'number' ? parseFloat(e.target.value) : e.target.value);
                }}
              />
            </div>
          );
        })}
      </div>
      
      {/* Output handles - Concentrated layout */}
      {data.outputs?.map((output: NodeOutput, index: number) => {
        const handleKey = output.id || output.name || `output-${index}`;
        const handleId = output.id || output.name || `output-${index}`;
        
        return (
          <Handle
            key={handleKey}
            type="source"
            position={Position.Right}
            id={`${handleId}-handle`}
            className="output-handle"
            style={getConcentratedHandlePosition(data.outputs, index)}
          />
        );
      })}
    </div>
  );
};

export default memo(MyNewNode);
```

## 检查清单
在提交新节点之前，请确保：
- [ ] 使用了`generic-node`类名
- [ ] 使用了集中式连接点布局
- [ ] 使用了统一的参数组布局
- [ ] 导入了必要的工具函数
- [ ] 节点外观与Stable Diffusion Generate节点一致

## 现有节点更新
如果需要更新现有节点以使用统一样式，请参考上述示例进行修改。
