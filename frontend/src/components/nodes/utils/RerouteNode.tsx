import React from 'react';
import { Handle, Position } from 'reactflow';
import { WorkflowNode, NodeInput, NodeOutput } from '../../../types';

interface RerouteNodeProps {
  data: WorkflowNode['data'];
}

const RerouteNode: React.FC<RerouteNodeProps> = ({ data }) => {
  const handleNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡到ReactFlow层，防止显示信息窗口
  };
  return (
    <div className="react-flow__node reroute-node" onClick={handleNodeClick}>
      {/* Input handles */}
      {data.inputs?.map((input: NodeInput) => (
        <Handle
          key={input.name}
          type="target"
          position={Position.Left}
          id={`${input.name}-handle`}
          className="node-handle"
          style={{ left: 0 }}
        />
      ))}
      
      <div className="node-header">
        <span>{data.label}</span>
      </div>
      
      <div className="node-content">
        <div className="node-description">
          Reroutes connections for better layout organization
        </div>
      </div>
      
      {/* Output handles */}
      {data.outputs?.map((output: NodeOutput) => (
        <Handle
          key={output.name}
          type="source"
          position={Position.Right}
          id={`${output.name}-handle`}
          className="node-handle"
          style={{ right: 0 }}
        />
      ))}
    </div>
  );
};

export default RerouteNode;