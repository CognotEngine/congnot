import React from 'react';
import { NodeParam } from '../../../types';

// 参数控件属性接口
interface ParamControlProps {
  param: NodeParam;
  paramName?: string;
  onChange: (value: any) => void;
}

// 滑块控件组件
const SliderControl: React.FC<ParamControlProps> = ({ param, onChange }) => {
  const widgetMeta = param.widget_meta || param.metadata?.widget_meta || {} as NodeParam['widget_meta'];
  return (
    <div className="param-group">
      <label className="param-label">{param.label}</label>
      <input
        type="range"
        min={widgetMeta?.min_value || 0}
        max={widgetMeta?.max_value || 100}
        step={widgetMeta?.step || param.step || 1}
        value={param.value || 0}
        className="node-slider"
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <span className="slider-value">{param.value}</span>
    </div>
  );
};

// 下拉框控件组件
const SelectControl: React.FC<ParamControlProps> = ({ param, onChange }) => {
  const widgetMeta = param.widget_meta || param.metadata?.widget_meta || {} as NodeParam['widget_meta'];
  const options = param.options || widgetMeta?.options || [];
  
  return (
    <div className="param-group">
      <label className="param-label">{param.label}</label>
      <select
        value={param.value || ''}
        className="node-select"
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((option: any, index: number) => (
          <option key={index} value={option.value || option}>
            {option.label || option}
          </option>
        ))}
      </select>
    </div>
  );
};

// 开关控件组件
const ToggleControl: React.FC<ParamControlProps> = ({ param, onChange }) => {
  return (
    <div className="param-group">
      <label className="toggle-label">
        <input
          type="checkbox"
          checked={param.value || false}
          className="node-toggle"
          onChange={(e) => onChange(e.target.checked)}
        />
        <span className="toggle-text">{param.label}</span>
      </label>
    </div>
  );
};

// 文本输入控件组件
const TextControl: React.FC<ParamControlProps> = ({ param, onChange }) => {
  return (
    <div className="param-group">
      <label className="param-label">{param.label}</label>
      <input
        type="text"
        value={param.value || ''}
        className="node-input"
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
};

// 数值输入控件组件
const NumberControl: React.FC<ParamControlProps> = ({ param, onChange }) => {
  const widgetMeta = param.widget_meta || param.metadata?.widget_meta || {} as NodeParam['widget_meta'];
  return (
    <div className="param-group">
      <label className="param-label">{param.label}</label>
      <input
        type="number"
        min={widgetMeta?.min_value}
        max={widgetMeta?.max_value}
        step={widgetMeta?.step || param.step || 1}
        value={param.value || 0}
        className="node-number-input"
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
};

// 参数控件工厂类
class ParamControlFactory {
  // 根据参数类型获取对应的控件组件
  static getControl(param: NodeParam, paramName: string, onChange: (value: any) => void) {
    const widgetMeta = param.widget_meta || param.metadata?.widget_meta || {} as NodeParam['widget_meta'];
    const widgetType = widgetMeta?.widget_type || param.type;
    
    switch (widgetType) {
      case 'slider':
        return <SliderControl key={paramName} param={param} paramName={paramName} onChange={onChange} />;
      case 'combo':
      case 'select':
        return <SelectControl key={paramName} param={param} paramName={paramName} onChange={onChange} />;
      case 'toggle':
      case 'boolean':
        return <ToggleControl key={paramName} param={param} paramName={paramName} onChange={onChange} />;
      case 'number':
        return <NumberControl key={paramName} param={param} paramName={paramName} onChange={onChange} />;
      case 'text':
      default:
        return <TextControl key={paramName} param={param} paramName={paramName} onChange={onChange} />;
    }
  }
}

export default ParamControlFactory;
export { SliderControl, SelectControl, ToggleControl, TextControl, NumberControl };
