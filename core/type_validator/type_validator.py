import typing
from typing import Any, Dict, List, Optional, Tuple, Type, Union

class TypeValidationError(Exception):
    
    def __init__(self, message: str, actual_type: Optional[type] = None, expected_type: Optional[type] = None):
        self.message = message
        self.actual_type = actual_type
        self.expected_type = expected_type
        super().__init__(message)

class TypeValidator:
    
    
    def __init__(self, strict: bool = True):
        
        self.strict = strict
        self.type_mappings = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'None': type(None)
        }
    
    def validate(self, data: Any, expected_type: Union[type, str, List[Union[type, str]]]) -> bool:
        
        try:
            return validate_type(data, expected_type, self.strict, self.type_mappings)
        except TypeValidationError:
            if self.strict:
                raise
            return False
    
    def validate_dict(self, data: Dict[str, Any], schema: Dict[str, Union[type, str, List[Union[type, str]]]]) -> bool:
        
        try:
            if not isinstance(data, dict):
                raise TypeValidationError("Data must be of type dict", type(data), dict)
            
            for field, expected_type in schema.items():
                if field not in data:
                    raise TypeValidationError(f"Missing required field: {field}")
                    
                field_data = data[field]
                if not validate_type(field_data, expected_type, self.strict, self.type_mappings):
                    raise TypeValidationError(
                        f"Type mismatch for field {field}",
                        type(field_data),
                        expected_type
                    )
            
            return True
        except TypeValidationError:
            if self.strict:
                raise
            return False
    
    def add_type_mapping(self, type_name: str, type_obj: type) -> None:
        
        self.type_mappings[type_name] = type_obj
    
    def get_supported_types(self) -> List[str]:
        
        return list(self.type_mappings.keys())

def validate_type(
    data: Any, 
    expected_type: Union[type, str, List[Union[type, str]]],
    strict: bool = True,
    type_mappings: Optional[Dict[str, type]] = None
) -> bool:
    
    if type_mappings is None:
        type_mappings = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'None': type(None)
        }
    
    
    if isinstance(expected_type, list):
        for type_item in expected_type:
            try:
                if validate_type(data, type_item, True, type_mappings):
                    return True
            except TypeValidationError:
                continue
        
        if strict:
            raise TypeValidationError(
                f"Data type {type(data).__name__} does not match expected type list {expected_type}",
                type(data),
                expected_type
            )
        return False
    
    
    if isinstance(expected_type, str):
        if expected_type not in type_mappings:
            if strict:
                raise TypeValidationError(f"Unsupported type name: {expected_type}")
            return False
        expected_type = type_mappings[expected_type]
    
    
    if expected_type is type(None) or expected_type == 'None':
        if data is None:
            return True
        if strict:
            raise TypeValidationError(f"Data type {type(data).__name__} does not match expected type None", type(data), None)
        return False
    
    
    if hasattr(expected_type, '__origin__'):
        
        if expected_type.__origin__ is list:
            if not isinstance(data, list):
                if strict:
                    raise TypeValidationError(f"Data type {type(data).__name__} does not match expected type List", type(data), list)
                return False
        
            if expected_type.__args__:
                item_type = expected_type.__args__[0]
                for item in data:
                    if not validate_type(item, item_type, strict, type_mappings):
                        return False
            return True
        
        
        elif expected_type.__origin__ is dict:
            if not isinstance(data, dict):
                if strict:
                    raise TypeValidationError(f"Data type {type(data).__name__} does not match expected type Dict", type(data), dict)
                return False
        
            if expected_type.__args__ and len(expected_type.__args__) == 2:
                key_type, value_type = expected_type.__args__
                for key, value in data.items():
                    if not validate_type(key, key_type, strict, type_mappings):
                        return False
                    if not validate_type(value, value_type, strict, type_mappings):
                        return False
            return True
        
        
        elif expected_type.__origin__ is tuple:
            if not isinstance(data, tuple):
                if strict:
                    raise TypeValidationError(f"Data type {type(data).__name__} does not match expected type Tuple", type(data), tuple)
                return False
        
            if expected_type.__args__:
                if len(data) != len(expected_type.__args__):
                    if strict:
                        raise TypeValidationError(f"Tuple length {len(data)} does not match expected length {len(expected_type.__args__)}")
                    return False
                    
                for i, (item, item_type) in enumerate(zip(data, expected_type.__args__)):
                    if not validate_type(item, item_type, strict, type_mappings):
                        return False
            return True
    
    
    if isinstance(data, expected_type):
        return True
    
    
    if not strict:
        if expected_type is int and isinstance(data, float) and data.is_integer():
            return True
        if expected_type is float and isinstance(data, int):
            return True
    
    
    if strict:
        raise TypeValidationError(
            f"Data type {type(data).__name__} does not match expected type {expected_type.__name__}",
            type(data),
            expected_type
        )
    return False