import { useEffect, useState } from 'react';
import './NodeWidget.css';

interface NodeWidgetProps {
  label?: string;
  type: 'text' | 'number' | 'slider' | 'combo' | 'boolean';
  value?: string | number | boolean;
  onChange?: (value: string | number | boolean) => void;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
  description?: string;
}

const NodeWidget = ({ 
  label, 
  type, 
  value, 
  onChange, 
  options = [], 
  min = 0, 
  max = 100, 
  step = 1,
  description = ''
}: NodeWidgetProps) => {
  
  const [widgetValue, setWidgetValue] = useState<string | number | boolean>(value || '');
  
  
  useEffect(() => {
    setWidgetValue(value || '');
  }, [value]);
  
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    let newValue: any;
    
    if (type === 'number' || type === 'slider') {
      newValue = parseFloat(e.target.value);
      
      if (type === 'slider') {
        setWidgetValue(newValue);
      }
    } else if (type === 'boolean') {
      newValue = (e.target as HTMLInputElement).checked;
    } else {
      newValue = e.target.value;
    }
    
    if (onChange) {
      onChange(newValue);
    }
  };
  
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setWidgetValue(newValue);
    
    
  };
  
  
  const handleInputBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value;
    
    if (type === 'number' || type === 'slider') {
      const numValue = parseFloat(newValue);
      let finalValue = numValue;
      
      if (finalValue < min) finalValue = min;
      if (finalValue > max) finalValue = max;
      
      if (onChange) {
        onChange(finalValue);
      }
    } else {
      if (onChange) {
        onChange(newValue);
      }
    }
  };
  
  
  const renderControl = () => {
    switch (type) {
      case 'text':
        return (
          <input
            type="text"
            value={widgetValue as string}
            onChange={handleChange}
            className="node-widget-input node-widget-input-text"
            placeholder="Enter text"
          />
        );
        
      case 'number':
        return (
          <input
            type="number"
            value={widgetValue as number}
            onChange={handleChange}
            className="node-widget-input node-widget-input-number"
            min={min}
            max={max}
            step={step}
          />
        );
        
      case 'slider':
        return (
          <div className="node-widget-slider-container">
            <input
              type="range"
              value={widgetValue as number}
              onChange={handleChange}
              className="node-widget-slider"
              min={min}
              max={max}
              step={step}
            />
            <input
              type="number"
              value={widgetValue as number}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              className="node-widget-input node-widget-input-small"
              min={min}
              max={max}
              step={step}
              style={{ width: '60px', marginLeft: '10px' }}
            />
          </div>
        );
        
      case 'combo':
        return (
          <select
            value={widgetValue as string}
            onChange={handleChange}
            className="node-widget-select"
          >
            {options.map((option, index) => (
              <option key={index} value={option}>
                {option}
              </option>
            ))}
          </select>
        );
        
      case 'boolean':
        return (
          <input
            type="checkbox"
            checked={widgetValue as boolean}
            onChange={handleChange}
            className="node-widget-checkbox"
          />
        );
        
      default:
        return (
          <input
            type="text"
            value={widgetValue as string}
            onChange={handleChange}
            className="node-widget-input"
            placeholder={`Unknown type: ${type}`}
          />
        );
    }
  };
  
  return (
    <div className="node-widget">
      {label && <div className="node-widget-label">{label}</div>}
      <div className="node-widget-control">
        {renderControl()}
      </div>
      {description && <div className="node-widget-description">{description}</div>}
    </div>
  );
};

export default NodeWidget;