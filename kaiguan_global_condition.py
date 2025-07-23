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
    支持手动设置和动态接收组名来控制组开关
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable_group": ("BOOLEAN", {"default": True}),
                "switch_mode": (["开启", "关闭", "屏蔽"], {"default": "开启"}),
                "group_names": ("STRING", {"default": "", "multiline": True, "placeholder": "手动输入组名\n多个组用换行分隔\n留空=控制所有组"}),
            },
            "optional": {
                "dynamic_group_names": (any_type, {"tooltip": "动态输入组名，支持字符串或列表格式"}),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("组状态", "操作结果", "受控组列表")
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, enable_group, switch_mode, group_names, dynamic_group_names=None):
        
        if not enable_group:
            return (False, "节点已禁用", "无")
        
        # 解析组名：优先使用动态输入，其次使用手动输入
        final_groups = self._parse_group_names(group_names, dynamic_group_names)
        
        # 根据模式确定操作
        action_map = {
            "开启": "启用组",
            "关闭": "禁用组", 
            "屏蔽": "屏蔽组"
        }
        action = action_map[switch_mode]
        
        # 生成组列表描述
        if final_groups:
            groups_desc = ", ".join(final_groups)
            groups_list_desc = f"指定组: {groups_desc}"
        else:
            groups_desc = "所有组"
            groups_list_desc = "所有组"
        
        result = f"{action}: {groups_desc}"
        
        print(f"🎯 智能组开关: {result}")
        print(f"   受控组详情: {groups_list_desc}")
        
        return (enable_group, result, groups_list_desc)
    
    def _parse_group_names(self, manual_groups, dynamic_groups):
        """解析组名，支持多种输入格式"""
        
        final_groups = []
        
        # 1. 优先处理动态输入的组名
        if dynamic_groups is not None:
            dynamic_parsed = self._parse_dynamic_input(dynamic_groups)
            if dynamic_parsed:
                final_groups.extend(dynamic_parsed)
                print(f"🎯 使用动态组名: {dynamic_parsed}")
        
        # 2. 如果没有动态输入，使用手动输入
        if not final_groups and manual_groups and manual_groups.strip():
            manual_parsed = [g.strip() for g in manual_groups.split('\n') if g.strip()]
            final_groups.extend(manual_parsed)
            print(f"🎯 使用手动组名: {manual_parsed}")
        
        return final_groups
    
    def _parse_dynamic_input(self, dynamic_input):
        """解析动态输入，支持多种格式"""
        
        if dynamic_input is None:
            return []
        
        try:
            # 1. 如果是列表格式
            if isinstance(dynamic_input, (list, tuple)):
                return [str(item).strip() for item in dynamic_input if str(item).strip()]
            
            # 2. 如果是字符串格式
            elif isinstance(dynamic_input, str):
                if dynamic_input.strip():
                    # 支持多种分隔符：换行、逗号、分号
                    if '\n' in dynamic_input:
                        return [g.strip() for g in dynamic_input.split('\n') if g.strip()]
                    elif ',' in dynamic_input:
                        return [g.strip() for g in dynamic_input.split(',') if g.strip()]
                    elif ';' in dynamic_input:
                        return [g.strip() for g in dynamic_input.split(';') if g.strip()]
                    else:
                        return [dynamic_input.strip()]
            
            # 3. 其他类型转字符串处理
            else:
                str_input = str(dynamic_input).strip()
                if str_input:
                    return [str_input]
        
        except Exception as e:
            print(f"🎯 动态组名解析错误: {e}")
        
        return []


class AdvancedGroupSwitchNode:
    """
    高级组开关节点：支持更复杂的组控制逻辑
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable": ("BOOLEAN", {"default": True}),
                "control_mode": (["单组控制", "多组控制", "全组控制"], {"default": "单组控制"}),
            },
            "optional": {
                "group_name": ("STRING", {"default": "", "placeholder": "单个组名"}),
                "group_list": (any_type, {"tooltip": "组名列表，支持字符串或列表格式"}),
                "enable_action": (["启用", "禁用", "屏蔽"], {"default": "启用"}),
                "disable_action": (["启用", "禁用", "屏蔽"], {"default": "禁用"}),
                "apply_enable": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("控制结果", "组列表", "执行状态")
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, enable, control_mode, group_name="", group_list=None, 
                enable_action="启用", disable_action="禁用", apply_enable=True):
        
        if not enable:
            return ("节点已禁用", "无", False)
        
        # 根据控制模式确定目标组
        target_groups = []
        
        if control_mode == "单组控制":
            if group_name.strip():
                target_groups = [group_name.strip()]
        elif control_mode == "多组控制":
            if group_list is not None:
                target_groups = self._parse_group_list(group_list)
        # 全组控制时 target_groups 保持空列表
        
        # 确定执行的动作
        action = f"{enable_action}组" if apply_enable else f"{disable_action}组"
        
        # 生成结果描述
        if target_groups:
            groups_desc = ", ".join(target_groups)
            result = f"{action}: {groups_desc}"
        else:
            groups_desc = "所有组"
            result = f"{action}: 所有组"
        
        print(f"🔧 高级组开关: {result}")
        
        return (result, groups_desc, True)
    
    def _parse_group_list(self, group_list):
        """解析组列表"""
        if group_list is None:
            return []
        
        try:
            if isinstance(group_list, (list, tuple)):
                return [str(item).strip() for item in group_list if str(item).strip()]
            elif isinstance(group_list, str):
                if ',' in group_list:
                    return [g.strip() for g in group_list.split(',') if g.strip()]
                elif '\n' in group_list:
                    return [g.strip() for g in group_list.split('\n') if g.strip()]
                else:
                    return [group_list.strip()] if group_list.strip() else []
        except:
            pass
        
        return []


class FlowBypassGroupNode:
    """
    流程屏蔽组节点：接收流程输入，屏蔽指定的组
    这是一个原子功能节点，专门用于在流程中屏蔽组
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "flow_input": (any_type,),  # 接收流程输入
                "groups_to_bypass": ("STRING", {"multiline": True, "placeholder": "要屏蔽的组名，支持多种分割方式：\n• 换行：组1\\n组2\n• 逗号：组1,组2\n• 分号：组1;组2\n• 竖线：组1|组2\n• 空格：组1 组2\n• 混合：自动识别"}),
            },
            "optional": {},
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("输出",)
    FUNCTION = "execute"
    CATEGORY = "2🐕kaiguan"

    def execute(self, flow_input, groups_to_bypass):
        """
        核心功能：屏蔽指定组，然后传递流程数据
        """
        
        # 解析要屏蔽的组名，支持多种分割方式
        groups_list = self._parse_groups_flexible(groups_to_bypass)
        
        # 输出调试信息
        if groups_list:
            print(f"🚫 流程屏蔽组: {', '.join(groups_list)}")
            print(f"   共屏蔽 {len(groups_list)} 个组")
        else:
            print("🚫 流程屏蔽组: 未指定组名，跳过屏蔽")
        
        # 直接传递流程输入到输出
        return (flow_input,)
    
    def _parse_groups_flexible(self, groups_input):
        """
        灵活解析组名，支持多种分割方式：
        - 换行分割: group1\ngroup2
        - 逗号分割: group1,group2
        - 分号分割: group1;group2
        - 竖线分割: group1|group2
        - 空格分割: group1 group2 (多个连续空格视为一个分割符)
        - 混合分割: 自动识别并处理
        """
        
        if not groups_input or not groups_input.strip():
            return []
        
        groups_text = groups_input.strip()
        groups_list = []
        
        # 1. 首先按换行分割
        lines = groups_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 2. 检查该行是否包含其他分割符
            if ',' in line:
                # 逗号分割
                parts = [part.strip() for part in line.split(',') if part.strip()]
                groups_list.extend(parts)
            elif ';' in line:
                # 分号分割
                parts = [part.strip() for part in line.split(';') if part.strip()]
                groups_list.extend(parts)
            elif '|' in line:
                # 竖线分割
                parts = [part.strip() for part in line.split('|') if part.strip()]
                groups_list.extend(parts)
            elif ' ' in line and len(line.split()) > 1:
                # 空格分割（多个词的情况）
                # 但要排除单个组名中间有空格的情况
                words = line.split()
                if len(words) > 1:
                    # 检查是否看起来像多个组名
                    if any(len(word) > 2 for word in words):  # 每个词长度大于2，可能是组名
                        groups_list.extend([word.strip() for word in words if word.strip()])
                    else:
                        # 可能是一个组名，保持原样
                        groups_list.append(line)
                else:
                    groups_list.append(line)
            else:
                # 单个组名
                groups_list.append(line)
        
        # 3. 去重并保持顺序
        seen = set()
        unique_groups = []
        for group in groups_list:
            if group and group not in seen:
                seen.add(group)
                unique_groups.append(group)
        
        return unique_groups


NODE_CLASS_MAPPINGS = {
    "GlobalGroupConditionNode": GlobalGroupConditionNode,
    "SmartGroupSwitchNode": SmartGroupSwitchNode,
    "AdvancedGroupSwitchNode": AdvancedGroupSwitchNode,
    "FlowBypassGroupNode": FlowBypassGroupNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GlobalGroupConditionNode": "全局组条件控制🌐🔀",
    "SmartGroupSwitchNode": "智能组开关🎯",
    "AdvancedGroupSwitchNode": "高级组开关🔧",
    "FlowBypassGroupNode": "流程屏蔽组🚫"
} 