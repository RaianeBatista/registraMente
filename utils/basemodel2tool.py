from enum import Enum
from types import UnionType
from typing import (
    List,
    Literal,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel
from pydantic.fields import FieldInfo


def get_field_type(field: FieldInfo) -> str:
    if field.annotation is None:
        return "any"
    return get_simple_type_name(field.annotation)


def get_simple_type_name(type_hint: type) -> str:
    """Get simplified OpenAI-compatible type name from Python type hint.
    
    Args:
        type_hint (type): Python type hint to convert
        
    Returns:
        str: OpenAI-compatible type name
    """
    # Add support for | type hint E.g. str | None
    if get_origin(type_hint) in (Union, UnionType) or isinstance(type_hint, UnionType):
        types = [t for t in get_args(type_hint) if t is not type(None)]
        if types:
            return get_simple_type_name(types[0])
        raise ValueError(f"Invalid Union type {type_hint}")

    if get_origin(type_hint) in (list, List):
        return "array"
    elif type_hint is str:
        return "string"
    elif type_hint is int:
        return "integer"
    elif type_hint is float:
        return "number"
    elif type_hint is bool:
        return "boolean"
    elif get_origin(type_hint) == Literal:
        return "string"  # Literal values will be handled as enum values
    elif isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
        return "object"  # Handle nested BaseModel classes
    else:
        raise ValueError(f"Type hint {type_hint} not supported.")


def base_model2tool(model: type[BaseModel]) -> dict:
    """Convert a Pydantic BaseModel to OpenAI function format.
    
    Args:
        model (type[BaseModel]): Pydantic model class to convert
        
    Returns:
        dict: OpenAI function-calling format dictionary
    """
    json_output = {
        "type": "function",
        "function": {
            "name": model.__name__,
            "description": model.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }

    required_properties = []

    for name, field in model.__fields__.items():
        prop_dict = {
            "type": get_field_type(field),
            "description": field.field_info.description or "",
        }

        if get_origin(field.annotation) in (list, List):
            prop_dict["type"] = "array"
            args = get_args(field.annotation)
            if args:
                prop_dict["items"] = {"type": get_simple_type_name(args[0])}

        # Em Pydantic v1, field.required indica se é obrigatório, ou field.default é PydanticUndefined
        if field.required: # Alterado de field.is_required()
            required_properties.append(name)

        if isinstance(field.annotation, type) and issubclass(field.annotation, Enum):
            prop_dict["enum"] = [str(e.value) for e in field.annotation]

        json_output["function"]["parameters"]["properties"][name] = prop_dict

    if required_properties:
        json_output["function"]["parameters"]["required"] = required_properties

    return json_output