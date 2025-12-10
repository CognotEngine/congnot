

from typing import Any, Dict, Type, Optional, List, Literal
from enum import Enum
from pydantic import BaseModel, Field

class WidgetType(str, Enum):
    HANDLE = "handle"           
    SLIDER = "slider"           
    COMBO = "combo"             
    TEXT_INPUT = "text_input"   
    TEXT_AREA = "text_area"     
    TOGGLE = "toggle"           

class FieldMetadata(BaseModel):
    
    widget_type: WidgetType = Field(..., description="前端应渲染的控件类型。")
    label: Optional[str] = Field(None, description="字段的标签文本。")
    
    
    min_value: Optional[float] = Field(None, description="滑块或数字输入的最小值。")
    max_value: Optional[float] = Field(None, description="滑块或数字输入的最大值。")
    step: Optional[float] = Field(None, description="滑块或数字输入的步长。")
    options: Optional[List[str]] = Field(None, description="下拉框的选项列表。")
    
    
    color_type: Optional[str] = Field(None, description="端口的颜色编码类型（如 'MODEL', 'IMAGE'）。")
    display_mode: Literal["widget", "handle", "auto"] = Field("auto", description="显示模式：自动/强制显示为控件或端口。")

class BaseNode:
    
    
    class Inputs(BaseModel):
        
        pass
    
    class Outputs(BaseModel):
        
        pass
    
    def __call__(self, **inputs) -> Dict[str, Any]:
        
        raise NotImplementedError("子类必须实现__call__方法")
    
    @classmethod
    def get_input_schema(cls) -> Dict[str, Any]:
        
        schema = cls.Inputs.model_json_schema()
        properties = schema.get("properties", {})
        
        
        for name, prop in properties.items():
            
            if name in cls.Inputs.model_fields:
                field = cls.Inputs.model_fields[name]
                if field.json_schema_extra:
                    prop["metadata"] = field.json_schema_extra
                
                
                
                widget_type = None
                display_mode = "auto"
                if field.json_schema_extra and "widget_meta" in field.json_schema_extra:
                    widget_type = field.json_schema_extra["widget_meta"].get("widget_type")
                    display_mode = field.json_schema_extra["widget_meta"].get("display_mode", "auto")
                
                
                has_default = field.default is not None or field.default_factory is not None
                
                # 确定字段的渲染方式
                if display_mode == "widget":
                    render_as = "widget"
                elif display_mode == "handle":
                    render_as = "handle"
                else:  # auto mode
                    render_as = "handle" if (widget_type == "handle" or not has_default) else "widget"
                
                
                if "metadata" not in prop:
                    prop["metadata"] = {}
                prop["metadata"]["render_as"] = render_as
        
        return {
            "properties": properties,
            "required": schema.get("required", [])
        }
    
    @classmethod
    def get_output_schema(cls) -> Dict[str, Any]:
        
        return cls.Outputs.model_json_schema()

def text_input(default: Any = None, description: str = "", label: Optional[str] = None, display_mode: Literal["widget", "handle", "auto"] = "auto") -> Any:
    
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "widget_meta": FieldMetadata(
                widget_type=WidgetType.TEXT_INPUT,
                label=label,
                display_mode=display_mode
            ).model_dump(by_alias=True)
        }
    )

def text_area(default: Any = None, description: str = "", label: Optional[str] = None, display_mode: Literal["widget", "handle", "auto"] = "auto") -> Any:
    
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "widget_meta": FieldMetadata(
                widget_type=WidgetType.TEXT_AREA,
                label=label,
                display_mode=display_mode
            ).model_dump(by_alias=True)
        }
    )

def toggle(default: bool = False, description: str = "", label: Optional[str] = None, display_mode: Literal["widget", "handle", "auto"] = "auto") -> bool:
    
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "widget_meta": FieldMetadata(
                widget_type=WidgetType.TOGGLE,
                label=label,
                display_mode=display_mode
            ).model_dump(by_alias=True)
        }
    )

def slider(default: float = 0, description: str = "", min: float = 0, max: float = 100, step: float = 1, label: Optional[str] = None, display_mode: Literal["widget", "handle", "auto"] = "auto") -> float:
    
    return Field(
        default=default,
        description=description,
        ge=min,
        le=max,
        json_schema_extra={
            "widget_meta": FieldMetadata(
                widget_type=WidgetType.SLIDER,
                min_value=min,
                max_value=max,
                step=step,
                label=label,
                display_mode=display_mode
            ).model_dump(by_alias=True)
        }
    )

def combo(default: Any = None, description: str = "", options: Optional[List[str]] = None, label: Optional[str] = None, display_mode: Literal["widget", "handle", "auto"] = "auto") -> Any:
    
    if options is None:
        options = []
    
    if default is None and options:
        default = options[0]
    
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "widget_meta": FieldMetadata(
                widget_type=WidgetType.COMBO,
                options=options,
                label=label,
                display_mode=display_mode
            ).model_dump(by_alias=True)
        }
    )

def handle(default: Any = None, description: str = "", color_type: Optional[str] = None, label: Optional[str] = None, display_mode: Literal["widget", "handle", "auto"] = "handle") -> Any:
    
    return Field(
        default=default,
        description=description,
        json_schema_extra={
            "widget_meta": FieldMetadata(
                widget_type=WidgetType.HANDLE,
                color_type=color_type,
                label=label,
                display_mode=display_mode
            ).model_dump(by_alias=True)
        }
    )
