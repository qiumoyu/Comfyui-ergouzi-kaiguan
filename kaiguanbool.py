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
    布尔跳过节点：根据布尔条件判断是否执行后续节点或控制节点组
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
                "control_type": (["跳过节点", "忽略组", "禁用组", "混合开关"], {"default": "跳过节点"}),
            },
            "optional": {},
        }

    RETURN_TYPES = (any_type, "*", "*", "*")
    RETURN_NAMES = ("输出", "忽略组", "禁用组", "混合开关")
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, condition, input, invert, control_type):
        # 如果invert为True，则反转条件
        if invert:
            condition = not condition
        
        # 打印调试信息
        print(f"布尔跳过节点: 条件={condition}, 反转={invert}, 控制类型={control_type}")
        
        # 根据控制类型和条件返回不同的输出
        if control_type == "跳过节点":
            if condition:
                return (input, None, None, None)
            else:
                return (None, None, None, None)
        elif control_type == "忽略组":
            return (input, condition, None, None)
        elif control_type == "禁用组":
            return (input, None, condition, None)
        elif control_type == "混合开关":
            return (input, None, None, condition)
        else:
            # 默认行为
            if condition:
                return (input, None, None, None)
            else:
                return (None, None, None, None)

NODE_CLASS_MAPPINGS = {
    "BooleanSkipNode": BooleanSkipNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BooleanSkipNode": "逻辑开关🔄"
}