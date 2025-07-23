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

class GlobalGroupConditionNode:
    """
    全局组条件控制节点：根据条件判断自动控制ComfyUI节点组的开关状态
    - 支持复杂条件判断
    - 智能控制节点组的启用/禁用/屏蔽状态
    - 可同时控制多个组或所有组
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable": ("BOOLEAN", {"default": True}),
                "input_value": (any_type,),
                "comparison_type": (["等于", "不等于", "大于", "小于", "大于等于", "小于等于", "包含", "不包含"], {"default": "等于"}),
                "comparison_value": ("STRING", {"default": ""}),
                "when_true": (["启用组", "禁用组", "屏蔽组", "不变"], {"default": "启用组"}),
                "when_false": (["启用组", "禁用组", "屏蔽组", "不变"], {"default": "禁用组"}),
                "target_groups": ("STRING", {"default": "", "multiline": True, "placeholder": "留空=控制所有组\n多个组名用换行分隔"}),
                "reverse_condition": ("BOOLEAN", {"default": False}),
            },
            "optional": {},
        }

    RETURN_TYPES = (any_type, "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("输出", "条件结果", "执行动作", "受控组列表")
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, enable, input_value, comparison_type, comparison_value, 
                when_true, when_false, target_groups, reverse_condition):
        
        # 如果节点被禁用，直接传递输入
        if not enable:
            return (input_value, False, "节点已禁用", "无")
        
        # 执行条件判断
        condition_result = self._evaluate_condition(input_value, comparison_type, comparison_value)
        
        # 是否反转条件
        if reverse_condition:
            condition_result = not condition_result
        
        # 根据条件结果选择动作
        action = when_true if condition_result else when_false
        
        # 解析目标组
        target_group_list = self._parse_target_groups(target_groups)
        
        # 执行组控制（这里只是返回控制信息，实际控制在前端JavaScript中完成）
        control_info = {
            'action': action,
            'groups': target_group_list,
            'condition_result': condition_result
        }
        
        # 生成受控组列表描述
        groups_desc = "所有组" if not target_group_list else ", ".join(target_group_list)
        
        # 调试输出
        print(f"🌐 全局组条件控制: 输入={input_value}, 条件={condition_result}, 动作={action}, 目标={groups_desc}")
        
        return (input_value, condition_result, action, groups_desc)
    
    def _evaluate_condition(self, input_value, comparison_type, comparison_value):
        """条件判断核心逻辑"""
        
        # 数据类型智能转换
        if isinstance(input_value, str):
            input_str = input_value
            input_int = convert_to_int(input_value)
            input_float = convert_to_float(input_value)
        else:
            input_str = convert_to_str(input_value)
            input_int = convert_to_int(input_str) if input_value is not None else None
            input_float = convert_to_float(input_str) if input_value is not None else None
        
        # 比较值转换
        comp_str = comparison_value
        comp_int = convert_to_int(comparison_value)
        comp_float = convert_to_float(comparison_value)
        
        # 执行比较操作
        try:
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
            
        except Exception as e:
            print(f"🌐 条件判断错误: {e}")
            return False
        
        return False
    
    def _parse_target_groups(self, target_groups):
        """解析目标组列表"""
        if not target_groups or not target_groups.strip():
            return []  # 空列表表示控制所有组
        
        return [group.strip() for group in target_groups.split('\n') if group.strip()]


class SmartGroupSwitchNode:
    """
    智能组开关节点：简化版的组控制节点
    直接接受布尔输入来控制组开关
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable_group": ("BOOLEAN", {"default": True}),
                "group_names": ("STRING", {"default": "", "multiline": True, "placeholder": "要控制的组名\n多个组用换行分隔\n留空=控制所有组"}),
                "switch_mode": (["开启", "关闭", "屏蔽"], {"default": "开启"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("组状态", "操作结果")
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, enable_group, group_names, switch_mode):
        # 解析组名
        if group_names.strip():
            groups = [g.strip() for g in group_names.split('\n') if g.strip()]
            groups_desc = ", ".join(groups)
        else:
            groups = []
            groups_desc = "所有组"
        
        # 根据模式确定操作
        action_map = {
            "开启": "启用组",
            "关闭": "禁用组", 
            "屏蔽": "屏蔽组"
        }
        action = action_map[switch_mode]
        
        result = f"{action}: {groups_desc}"
        
        print(f"🎯 智能组开关: {result}")
        
        return (enable_group, result)


NODE_CLASS_MAPPINGS = {
    "GlobalGroupConditionNode": GlobalGroupConditionNode,
    "SmartGroupSwitchNode": SmartGroupSwitchNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GlobalGroupConditionNode": "全局组条件控制🌐🔀",
    "SmartGroupSwitchNode": "智能组开关🎯"
} 