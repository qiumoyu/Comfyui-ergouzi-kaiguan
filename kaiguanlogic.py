def is_context_empty(ctx):
    return not ctx or all(v is None for v in ctx.values())

def get_name(name):
    return '{}'.format(name)

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

def is_none(value):
    if value is not None:
        if isinstance(value, dict) and 'model' in value and 'clip' in value:
            return is_context_empty(value)
    return value is None

def convert_to_int(value):
    try:
        return int(value)
    except ValueError:
        return None

def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return None

def convert_to_str(value):
    return str(value)

class LogicSkipNode:
    """
    逻辑跳过节点组：根据条件判断是否执行后续节点
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "input": (any_type,),
                "comparison_type": (["等于", "不等于", "大于", "小于", "大于等于", "小于等于", "包含", "不包含"], {"default": "等于"}),
                "comparison_value": ("STRING", {"default": ""}),
            },
            "optional": {},
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, condition, input, comparison_type, comparison_value):
        # 如果条件为False，直接返回输入，不进行逻辑判断
        if not condition:
            return (input,)
        
        # 将输入值转换为可比较的格式
        input_value = input
        if isinstance(input, str):
            input_str = input
            input_int = convert_to_int(input)
            input_float = convert_to_float(input)
        else:
            input_str = convert_to_str(input)
            input_int = convert_to_int(input_str) if input is not None else None
            input_float = convert_to_float(input_str) if input is not None else None
        
        # 将比较值转换为可比较的格式
        comp_str = comparison_value
        comp_int = convert_to_int(comparison_value)
        comp_float = convert_to_float(comparison_value)
        
        # 根据比较类型进行判断
        result = False
        
        if comparison_type == "等于":
            if comp_int is not None and input_int is not None:
                result = input_int == comp_int
            elif comp_float is not None and input_float is not None:
                result = input_float == comp_float
            else:
                result = input_str == comp_str
        
        elif comparison_type == "不等于":
            if comp_int is not None and input_int is not None:
                result = input_int != comp_int
            elif comp_float is not None and input_float is not None:
                result = input_float != comp_float
            else:
                result = input_str != comp_str
        
        elif comparison_type == "大于":
            if comp_int is not None and input_int is not None:
                result = input_int > comp_int
            elif comp_float is not None and input_float is not None:
                result = input_float > comp_float
            else:
                result = input_str > comp_str
        
        elif comparison_type == "小于":
            if comp_int is not None and input_int is not None:
                result = input_int < comp_int
            elif comp_float is not None and input_float is not None:
                result = input_float < comp_float
            else:
                result = input_str < comp_str
        
        elif comparison_type == "大于等于":
            if comp_int is not None and input_int is not None:
                result = input_int >= comp_int
            elif comp_float is not None and input_float is not None:
                result = input_float >= comp_float
            else:
                result = input_str >= comp_str
        
        elif comparison_type == "小于等于":
            if comp_int is not None and input_int is not None:
                result = input_int <= comp_int
            elif comp_float is not None and input_float is not None:
                result = input_float <= comp_float
            else:
                result = input_str <= comp_str
        
        elif comparison_type == "包含":
            result = comp_str in input_str
        
        elif comparison_type == "不包含":
            result = comp_str not in input_str
        
        # 打印调试信息
        print(f"逻辑跳过节点: 输入值={input_value}, 比较类型={comparison_type}, 比较值={comparison_value}, 结果={result}")
        
        # 根据结果返回输入或None
        if result:
            return (input,)
        else:
            return (None,)

NODE_CLASS_MAPPINGS = {
    "LogicSkipNode": LogicSkipNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LogicSkipNode": "逻辑跳过🔀"
}