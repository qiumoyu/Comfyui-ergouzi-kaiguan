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

class GlobalConditionControlNode:
    """
    全局条件控制节点：根据条件判断动态控制所有节点组的执行状态
    支持复杂条件判断和多种控制模式
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable_control": ("BOOLEAN", {"default": True}),
                "input_value": (any_type,),
                "comparison_type": (["等于", "不等于", "大于", "小于", "大于等于", "小于等于", "包含", "不包含"], {"default": "等于"}),
                "comparison_value": ("STRING", {"default": ""}),
                "control_mode": (["智能控制", "全部忽略", "全部禁用", "全部启用", "条件控制"], {"default": "条件控制"}),
                "condition_true_action": (["启用", "忽略", "禁用"], {"default": "启用"}),
                "condition_false_action": (["启用", "忽略", "禁用"], {"default": "禁用"}),
                "target_groups": ("STRING", {"default": "", "multiline": True, "placeholder": "留空控制所有组，或输入组名（每行一个）"}),
                "invert_condition": ("BOOLEAN", {"default": False}),
            },
            "optional": {},
        }

    RETURN_TYPES = (any_type, "BOOLEAN", "STRING")
    RETURN_NAMES = ("输出", "条件结果", "控制状态")
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, enable_control, input_value, comparison_type, comparison_value, 
                control_mode, condition_true_action, condition_false_action, 
                target_groups, invert_condition):
        
        # 如果控制被禁用，直接返回输入值
        if not enable_control:
            return (input_value, True, "控制已禁用")
        
        # 解析目标组列表
        target_group_list = []
        if target_groups.strip():
            target_group_list = [group.strip() for group in target_groups.split('\n') if group.strip()]
        
        # 执行条件判断
        condition_result = self._evaluate_condition(input_value, comparison_type, comparison_value)
        
        # 如果需要反转条件
        if invert_condition:
            condition_result = not condition_result
        
        # 根据控制模式执行相应操作
        control_status = self._execute_control(control_mode, condition_result, 
                                             condition_true_action, condition_false_action, 
                                             target_group_list)
        
        # 打印调试信息
        print(f"全局条件控制节点: 输入值={input_value}, 比较类型={comparison_type}, "
              f"比较值={comparison_value}, 条件结果={condition_result}, "
              f"控制模式={control_mode}, 控制状态={control_status}")
        
        return (input_value, condition_result, control_status)
    
    def _evaluate_condition(self, input_value, comparison_type, comparison_value):
        """评估条件判断"""
        # 将输入值转换为可比较的格式
        if isinstance(input_value, str):
            input_str = input_value
            input_int = convert_to_int(input_value)
            input_float = convert_to_float(input_value)
        else:
            input_str = convert_to_str(input_value)
            input_int = convert_to_int(input_str) if input_value is not None else None
            input_float = convert_to_float(input_str) if input_value is not None else None
        
        # 将比较值转换为可比较的格式
        comp_str = comparison_value
        comp_int = convert_to_int(comparison_value)
        comp_float = convert_to_float(comparison_value)
        
        # 根据比较类型进行判断
        if comparison_type == "等于":
            if comp_int is not None and input_int is not None:
                return input_int == comp_int
            elif comp_float is not None and input_float is not None:
                return input_float == comp_float
            else:
                return input_str == comp_str
        
        elif comparison_type == "不等于":
            if comp_int is not None and input_int is not None:
                return input_int != comp_int
            elif comp_float is not None and input_float is not None:
                return input_float != comp_float
            else:
                return input_str != comp_str
        
        elif comparison_type == "大于":
            if comp_int is not None and input_int is not None:
                return input_int > comp_int
            elif comp_float is not None and input_float is not None:
                return input_float > comp_float
            else:
                return input_str > comp_str
        
        elif comparison_type == "小于":
            if comp_int is not None and input_int is not None:
                return input_int < comp_int
            elif comp_float is not None and input_float is not None:
                return input_float < comp_float
            else:
                return input_str < comp_str
        
        elif comparison_type == "大于等于":
            if comp_int is not None and input_int is not None:
                return input_int >= comp_int
            elif comp_float is not None and input_float is not None:
                return input_float >= comp_float
            else:
                return input_str >= comp_str
        
        elif comparison_type == "小于等于":
            if comp_int is not None and input_int is not None:
                return input_int <= comp_int
            elif comp_float is not None and input_float is not None:
                return input_float <= comp_float
            else:
                return input_str <= comp_str
        
        elif comparison_type == "包含":
            return comp_str in input_str
        
        elif comparison_type == "不包含":
            return comp_str not in input_str
        
        return False
    
    def _execute_control(self, control_mode, condition_result, condition_true_action, 
                        condition_false_action, target_group_list):
        """执行控制操作"""
        
        if control_mode == "智能控制":
            # 智能控制：根据条件结果自动选择最优操作
            if condition_result:
                action = "启用"
            else:
                action = "忽略"
        elif control_mode == "全部忽略":
            action = "忽略"
        elif control_mode == "全部禁用":
            action = "禁用"
        elif control_mode == "全部启用":
            action = "启用"
        elif control_mode == "条件控制":
            # 根据条件结果选择对应的动作
            if condition_result:
                action = condition_true_action
            else:
                action = condition_false_action
        else:
            action = "启用"
        
        # 这里返回控制状态描述，实际的组控制需要在前端JavaScript中实现
        if target_group_list:
            groups_info = f"目标组: {', '.join(target_group_list)}"
        else:
            groups_info = "所有组"
        
        return f"{action} - {groups_info}"


class GlobalConditionGroupControlNode:
    """
    全局条件组控制节点：专门用于连接到节点组的控制节点
    与GlobalConditionControlNode配合使用
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "control_signal": ("BOOLEAN", {"default": True}),
                "control_type": (["启用", "忽略", "禁用"], {"default": "启用"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("*",)
    FUNCTION = "process"
    CATEGORY = "2🐕kaiguan"

    def process(self, control_signal, control_type):
        """处理控制信号"""
        print(f"全局条件组控制: 控制信号={control_signal}, 控制类型={control_type}")
        return (control_signal,)


NODE_CLASS_MAPPINGS = {
    "GlobalConditionControlNode": GlobalConditionControlNode,
    "GlobalConditionGroupControlNode": GlobalConditionGroupControlNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GlobalConditionControlNode": "全局条件控制🌐🔀",
    "GlobalConditionGroupControlNode": "条件组控制🎯"
} 