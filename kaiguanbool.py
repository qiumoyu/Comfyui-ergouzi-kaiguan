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

class BooleanSkipNode:
    """
    布尔跳过节点：根据布尔条件判断是否执行后续节点
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "input": (any_type,),
                "invert": ("BOOLEAN", {"default": False}),
            },
            "optional": {},
        }

    RETURN_TYPES = (any_type,)
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, condition, input, invert):
        # 如果invert为True，则反转条件
        if invert:
            condition = not condition
        
        # 打印调试信息
        print(f"布尔跳过节点: 条件={condition}, 反转={invert}")
        
        # 根据条件返回输入或None
        if condition:
            return (input,)
        else:
            return (None,)

NODE_CLASS_MAPPINGS = {
    "BooleanSkipNode": BooleanSkipNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BooleanSkipNode": "布尔跳过🔄"
}