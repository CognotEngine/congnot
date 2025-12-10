import { NodeInput, NodeOutput } from '../types';

/**
 * Calculate fixed positions for handles on node edge
 * @param items Array of input or output ports
 * @param index Index of the current port
 * @param offsetY Vertical offset in pixels from top of node
 * @param spacing Vertical spacing in pixels between ports
 * @returns Style object with top position
 */
export const getConcentratedHandlePosition = (
  items: (NodeInput | NodeOutput)[] | number,
  index: number = 0,
  offsetY: number = 20,
  spacing: number = 25
): React.CSSProperties => {
  // Handle backward compatibility - if first parameter is a number, it's the index
  if (typeof items === 'number') {
    const top = offsetY + (items * spacing);
    return { top: `${top}px` };
  }
  
  // Position handles with fixed pixel spacing from top
  // Each handle is positioned 20px + index * 25px from the top
  const top = offsetY + (index * spacing);
  
  return { top: `${top}px` };
};
