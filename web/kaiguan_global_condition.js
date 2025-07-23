import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

// 全局组控制状态管理器
class GroupControlManager {
    constructor() {
        this.activeControllers = new Map(); // 活跃的控制节点
        this.groupStates = new Map();       // 组状态记录
        this.originalStates = new Map();    // 原始状态备份
    }
    
    // 注册控制节点
    registerController(nodeId, controlInfo) {
        this.activeControllers.set(nodeId, controlInfo);
        console.log(`🌐 注册组控制器: ${nodeId}`, controlInfo);
    }
    
    // 注销控制节点
    unregisterController(nodeId) {
        this.activeControllers.delete(nodeId);
        console.log(`🌐 注销组控制器: ${nodeId}`);
    }
    
    // 执行组控制
    executeGroupControl(action, targetGroups) {
        const allGroups = app.graph._groups || [];
        
        // 确定要控制的组
        const groupsToControl = targetGroups.length === 0 ? 
            allGroups : 
            allGroups.filter(group => targetGroups.includes(group.title));
        
        if (groupsToControl.length === 0) {
            console.warn('🌐 没有找到要控制的组');
            return;
        }
        
        console.log(`🌐 执行组控制: ${action} -> [${groupsToControl.map(g => g.title).join(', ')}]`);
        
        groupsToControl.forEach(group => {
            this.controlGroup(group, action);
        });
        
        // 刷新画布
        app.graph.setDirtyCanvas(true, true);
    }
    
    // 控制单个组
    controlGroup(group, action) {
        // 备份原始状态（如果还没有备份的话）
        if (!this.originalStates.has(group.title)) {
            this.backupGroupState(group);
        }
        
        // 重新计算组内节点
        group.recomputeInsideNodes();
        
        // 应用控制动作
        group._nodes.forEach(node => {
            if (!node) return;
            
            // 跳过控制节点自身，避免控制冲突
            if (this.isControlNode(node)) {
                return;
            }
            
            // 应用节点状态
            switch (action) {
                case "启用组":
                    node.mode = LiteGraph.ALWAYS;  // 0 - 正常执行
                    break;
                case "禁用组":
                    node.mode = LiteGraph.NEVER;   // 1 - 禁用（完全关闭）
                    break;
                case "屏蔽组":
                    node.mode = 4;                 // 4 - 屏蔽（跳过但传递数据）
                    break;
                case "不变":
                    // 不做任何改变
                    break;
                default:
                    console.warn(`🌐 未知控制动作: ${action}`);
            }
        });
        
        // 记录组状态
        this.groupStates.set(group.title, action);
    }
    
    // 备份组的原始状态
    backupGroupState(group) {
        const backup = [];
        group._nodes.forEach(node => {
            if (node) {
                backup.push({
                    nodeId: node.id,
                    originalMode: node.mode
                });
            }
        });
        this.originalStates.set(group.title, backup);
    }
    
    // 恢复组的原始状态
    restoreGroupState(groupTitle) {
        const backup = this.originalStates.get(groupTitle);
        if (!backup) {
            console.warn(`🌐 没有找到组 ${groupTitle} 的备份状态`);
            return;
        }
        
        backup.forEach(nodeBackup => {
            const node = app.graph.getNodeById(nodeBackup.nodeId);
            if (node) {
                node.mode = nodeBackup.originalMode;
            }
        });
        
        this.groupStates.delete(groupTitle);
        console.log(`🌐 恢复组状态: ${groupTitle}`);
    }
    
    // 恢复所有组状态
    restoreAllGroups() {
        this.originalStates.forEach((backup, groupTitle) => {
            this.restoreGroupState(groupTitle);
        });
        this.originalStates.clear();
        this.groupStates.clear();
        app.graph.setDirtyCanvas(true, true);
    }
    
    // 判断是否为控制节点
    isControlNode(node) {
        return node.type && (
            node.type.includes('GlobalGroupCondition') ||
            node.type.includes('SmartGroupSwitch') ||
            node.type.includes('Switch') ||
            node.type.includes('kaiguan') ||
            node.type.toLowerCase().includes('hulue') ||
            node.type.toLowerCase().includes('jinyong')
        );
    }
    
    // 获取状态信息
    getStatusInfo() {
        return {
            activeControllers: this.activeControllers.size,
            controlledGroups: this.groupStates.size,
            groupStates: Array.from(this.groupStates.entries()),
            hasBackups: this.originalStates.size > 0
        };
    }
}

// 全局管理器实例
const groupManager = new GroupControlManager();

// 解析目标组列表
function parseTargetGroups(groupsText) {
    if (!groupsText || !groupsText.trim()) {
        return [];
    }
    return groupsText.split('\n')
        .map(group => group.trim())
        .filter(group => group.length > 0);
}

// 处理组条件控制节点的执行
function handleGroupConditionControl(node) {
    const widgets = node.widgets;
    if (!widgets) return;
    
    // 获取节点参数
    const enable = widgets.find(w => w.name === "enable")?.value ?? true;
    if (!enable) {
        console.log('🌐 全局组条件控制已禁用');
        return;
    }
    
    const targetGroups = widgets.find(w => w.name === "target_groups")?.value ?? "";
    const whenTrue = widgets.find(w => w.name === "when_true")?.value ?? "启用组";
    const whenFalse = widgets.find(w => w.name === "when_false")?.value ?? "禁用组";
    
    // 从节点的输出获取条件结果（如果可用）
    const conditionResult = node.properties?.lastConditionResult ?? true;
    
    // 确定要执行的动作
    const action = conditionResult ? whenTrue : whenFalse;
    
    // 解析目标组
    const targetGroupList = parseTargetGroups(targetGroups);
    
    // 注册控制器
    groupManager.registerController(node.id, {
        action: action,
        targetGroups: targetGroupList,
        conditionResult: conditionResult
    });
    
    // 执行控制
    if (action !== "不变") {
        groupManager.executeGroupControl(action, targetGroupList);
    }
}

// 处理智能组开关节点
function handleSmartGroupSwitch(node) {
    const widgets = node.widgets;
    if (!widgets) return;
    
    const enableGroup = widgets.find(w => w.name === "enable_group")?.value ?? true;
    const groupNames = widgets.find(w => w.name === "group_names")?.value ?? "";
    const switchMode = widgets.find(w => w.name === "switch_mode")?.value ?? "开启";
    
    if (!enableGroup) {
        console.log('🎯 智能组开关已禁用');
        return;
    }
    
    // 获取动态组名输入（如果有连接）
    let dynamicGroupNames = null;
    if (node.inputs && node.inputs.length > 0) {
        // 查找dynamic_group_names输入
        const dynamicInput = node.inputs.find(input => input.name === "dynamic_group_names");
        if (dynamicInput && dynamicInput.link) {
            // 这里可以获取连接的数据，但在前端我们主要关注控制逻辑
            console.log('🎯 检测到动态组名输入连接');
        }
    }
    
    // 模式映射
    const actionMap = {
        "开启": "启用组",
        "关闭": "禁用组",
        "屏蔽": "屏蔽组"
    };
    
    const action = actionMap[switchMode];
    const targetGroups = parseTargetGroups(groupNames);
    
    // 注册控制器
    groupManager.registerController(node.id, {
        action: action,
        targetGroups: targetGroups,
        switchMode: switchMode,
        hasDynamicInput: dynamicGroupNames !== null
    });
    
    // 执行控制
    groupManager.executeGroupControl(action, targetGroups);
}

// 处理高级组开关节点
function handleAdvancedGroupSwitch(node) {
    const widgets = node.widgets;
    if (!widgets) return;
    
    const enable = widgets.find(w => w.name === "enable")?.value ?? true;
    const controlMode = widgets.find(w => w.name === "control_mode")?.value ?? "单组控制";
    const groupName = widgets.find(w => w.name === "group_name")?.value ?? "";
    const enableAction = widgets.find(w => w.name === "enable_action")?.value ?? "启用";
    const disableAction = widgets.find(w => w.name === "disable_action")?.value ?? "禁用";
    const applyEnable = widgets.find(w => w.name === "apply_enable")?.value ?? true;
    
    if (!enable) {
        console.log('🔧 高级组开关已禁用');
        return;
    }
    
    let targetGroups = [];
    let action = "";
    
    // 根据控制模式确定目标组和动作
    if (controlMode === "单组控制") {
        if (groupName.trim()) {
            targetGroups = [groupName.trim()];
        }
    } else if (controlMode === "多组控制") {
        // 检查是否有group_list输入连接
        if (node.inputs) {
            const groupListInput = node.inputs.find(input => input.name === "group_list");
            if (groupListInput && groupListInput.link) {
                console.log('🔧 检测到组列表输入连接');
                // 实际的组列表会在后端处理
            }
        }
    }
    // 全组控制时targetGroups保持空数组
    
    // 确定执行动作
    action = applyEnable ? `${enableAction}组` : `${disableAction}组`;
    
    // 注册控制器
    groupManager.registerController(node.id, {
        action: action,
        targetGroups: targetGroups,
        controlMode: controlMode,
        applyEnable: applyEnable
    });
    
    // 执行控制
    groupManager.executeGroupControl(action, targetGroups);
}

// 创建控制面板
function createControlPanel(node) {
    const dialog = document.createElement("div");
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 20px;
        background: linear-gradient(135deg, #2c3e50, #3498db);
        color: white;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 1000;
        max-height: 80vh;
        overflow-y: auto;
        width: 500px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    // 标题
    const title = document.createElement("h2");
    title.textContent = "🌐 全局组控制面板";
    title.style.cssText = "margin-top: 0; text-align: center; color: #ecf0f1;";
    dialog.appendChild(title);
    
    // 状态信息
    const statusInfo = groupManager.getStatusInfo();
    const statusDiv = document.createElement("div");
    statusDiv.style.cssText = `
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    `;
    
    statusDiv.innerHTML = `
        <h3 style="margin-top: 0; color: #f39c12;">📊 当前状态</h3>
        <p>🎮 活跃控制器: <strong>${statusInfo.activeControllers}</strong></p>
        <p>🎯 受控组数量: <strong>${statusInfo.controlledGroups}</strong></p>
        <p>💾 备份状态: <strong>${statusInfo.hasBackups ? '是' : '否'}</strong></p>
    `;
    dialog.appendChild(statusDiv);
    
    // 组状态列表
    if (statusInfo.groupStates.length > 0) {
        const groupDiv = document.createElement("div");
        groupDiv.style.cssText = `
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            max-height: 200px;
            overflow-y: auto;
        `;
        
        let groupHtml = "<h3 style='margin-top: 0; color: #e74c3c;'>🎛️ 组控制状态</h3>";
        statusInfo.groupStates.forEach(([groupName, action]) => {
            const statusColor = 
                action === "启用组" ? "#27ae60" :
                action === "屏蔽组" ? "#f39c12" : "#e74c3c";
            groupHtml += `<p style="color: ${statusColor};">▶ ${groupName}: ${action}</p>`;
        });
        
        groupDiv.innerHTML = groupHtml;
        dialog.appendChild(groupDiv);
    }
    
    // 快速控制按钮
    const quickControlDiv = document.createElement("div");
    quickControlDiv.innerHTML = "<h3 style='color: #9b59b6;'>⚡ 快速控制</h3>";
    dialog.appendChild(quickControlDiv);
    
    const buttonStyle = `
        margin: 5px;
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    `;
    
    const controls = [
        { text: "🟢 全部启用", action: "启用组", color: "#27ae60" },
        { text: "🟡 全部屏蔽", action: "屏蔽组", color: "#f39c12" },
        { text: "🔴 全部禁用", action: "禁用组", color: "#e74c3c" },
        { text: "🔄 恢复原状", action: "restore", color: "#95a5a6" }
    ];
    
    controls.forEach(control => {
        const btn = document.createElement("button");
        btn.textContent = control.text;
        btn.style.cssText = buttonStyle + `background-color: ${control.color}; color: white;`;
        
        btn.addEventListener("mouseenter", () => {
            btn.style.transform = "scale(1.05)";
            btn.style.boxShadow = "0 5px 15px rgba(0,0,0,0.3)";
        });
        
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "scale(1)";
            btn.style.boxShadow = "none";
        });
        
        btn.addEventListener("click", () => {
            if (control.action === "restore") {
                groupManager.restoreAllGroups();
            } else {
                groupManager.executeGroupControl(control.action, []);
            }
            document.body.removeChild(dialog);
        });
        
        quickControlDiv.appendChild(btn);
    });
    
    // 关闭按钮
    const closeBtn = document.createElement("button");
    closeBtn.textContent = "❌ 关闭";
    closeBtn.style.cssText = buttonStyle + `
        background-color: #34495e;
        color: white;
        width: 100%;
        margin-top: 20px;
    `;
    closeBtn.addEventListener("click", () => {
        document.body.removeChild(dialog);
    });
    dialog.appendChild(closeBtn);
    
    // 作者信息
    const authorBtn = document.createElement("button");
    authorBtn.textContent = "👨‍💻 灵仙儿和二狗子";
    authorBtn.style.cssText = `
        position: absolute;
        top: 15px;
        right: 15px;
        background: linear-gradient(45deg, #ff6b6b, #ffd93d);
        color: #2c3e50;
        border: none;
        padding: 8px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: bold;
        font-size: 12px;
    `;
    authorBtn.addEventListener("click", () => {
        window.open("https://space.bilibili.com/19723588", "_blank");
    });
    dialog.appendChild(authorBtn);
    
    document.body.appendChild(dialog);
}

// 扩展节点右键菜单
let originalGetNodeMenuOptions = LGraphCanvas.prototype.getNodeMenuOptions;
LGraphCanvas.prototype.getNodeMenuOptions = function(node) {
    const options = originalGetNodeMenuOptions.apply(this, arguments);
    
    if (node.type === "GlobalGroupConditionNode" || 
        node.type === "SmartGroupSwitchNode" || 
        node.type === "AdvancedGroupSwitchNode") {
        
        options.push(null); // 分割线
        
        options.push({
            content: "🌐 控制面板",
            callback: () => createControlPanel(node)
        });
        
        options.push({
            content: "🔄 立即执行",
            callback: () => {
                if (node.type === "GlobalGroupConditionNode") {
                    handleGroupConditionControl(node);
                } else if (node.type === "SmartGroupSwitchNode") {
                    handleSmartGroupSwitch(node);
                } else if (node.type === "AdvancedGroupSwitchNode") {
                    handleAdvancedGroupSwitch(node);
                }
            }
        });
        
        options.push({
            content: "🧹 清理状态",
            callback: () => {
                groupManager.unregisterController(node.id);
                groupManager.restoreAllGroups();
            }
        });
    }
    
    return options;
};

// 注册ComfyUI扩展
app.registerExtension({
    name: "Comfy.GlobalGroupControl",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 全局组条件控制节点
        if (nodeData.name === "GlobalGroupConditionNode") {
            
            nodeType.prototype.onNodeCreated = function() {
                this.properties = this.properties || {
                    lastConditionResult: true
                };
                
                // 监听widget变化
                setTimeout(() => {
                    this.widgets?.forEach(widget => {
                        const originalCallback = widget.callback;
                        widget.callback = (value) => {
                            if (originalCallback) originalCallback(value);
                            
                            // 延迟执行，确保所有参数都已更新
                            setTimeout(() => {
                                handleGroupConditionControl(this);
                            }, 50);
                        };
                    });
                }, 100);
            };
            
            nodeType.prototype.onSerialize = function(info) {
                info.properties = this.properties;
            };
            
            nodeType.prototype.onConfigure = function(info) {
                this.properties = info.properties || { lastConditionResult: true };
            };
            
            // 节点被删除时的清理
            nodeType.prototype.onRemoved = function() {
                groupManager.unregisterController(this.id);
            };
        }
        
        // 智能组开关节点
        if (nodeData.name === "SmartGroupSwitchNode") {
            
            nodeType.prototype.onNodeCreated = function() {
                // 监听widget变化
                setTimeout(() => {
                    this.widgets?.forEach(widget => {
                        const originalCallback = widget.callback;
                        widget.callback = (value) => {
                            if (originalCallback) originalCallback(value);
                            
                            setTimeout(() => {
                                handleSmartGroupSwitch(this);
                            }, 50);
                        };
                    });
                }, 100);
            };
            
            nodeType.prototype.onRemoved = function() {
                groupManager.unregisterController(this.id);
            };
        }
        
        // 高级组开关节点
        if (nodeData.name === "AdvancedGroupSwitchNode") {
            
            nodeType.prototype.onNodeCreated = function() {
                // 监听widget变化
                setTimeout(() => {
                    this.widgets?.forEach(widget => {
                        const originalCallback = widget.callback;
                        widget.callback = (value) => {
                            if (originalCallback) originalCallback(value);
                            
                            setTimeout(() => {
                                handleAdvancedGroupSwitch(this);
                            }, 50);
                        };
                    });
                }, 100);
            };
            
            nodeType.prototype.onRemoved = function() {
                groupManager.unregisterController(this.id);
            };
        }
    }
});

// 定期清理无效节点引用
setInterval(() => {
    const validNodeIds = new Set(app.graph._nodes.map(node => node.id));
    
    // 清理已删除的控制节点
    for (const [nodeId] of groupManager.activeControllers) {
        if (!validNodeIds.has(nodeId)) {
            groupManager.unregisterController(nodeId);
        }
    }
}, 10000);

console.log("🌐 全局组条件控制扩展已加载完成！");
console.log("   支持功能:");
console.log("   • 条件判断自动控制组开关");
console.log("   • 组状态管理（启用/禁用/屏蔽）"); 
console.log("   • 智能组开关控制");
console.log("   • 可视化控制面板"); 