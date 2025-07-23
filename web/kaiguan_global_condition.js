import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

// 全局条件控制状态管理
let globalConditionState = {
    activeNodes: new Set(),
    groupStates: new Map(),
    lastControlMode: null
};

function parseTargetGroups(targetGroupsText) {
    if (!targetGroupsText || !targetGroupsText.trim()) {
        return [];
    }
    return targetGroupsText.split('\n')
        .map(group => group.trim())
        .filter(group => group.length > 0);
}

function applyGroupControl(action, targetGroups) {
    const allGroups = app.graph._groups || [];
    
    // 如果没有指定目标组，则控制所有组
    const groupsToControl = targetGroups.length === 0 ? 
        allGroups : 
        allGroups.filter(group => targetGroups.includes(group.title));
    
    console.log(`全局条件控制: 执行动作 "${action}" 于 ${groupsToControl.length} 个组`, 
                groupsToControl.map(g => g.title));
    
    groupsToControl.forEach(group => {
        // 重新计算组内节点
        group.recomputeInsideNodes();
        
        // 应用控制动作到组内所有节点
        group._nodes.forEach(node => {
            if (!node) return;
            
            // 跳过开关控制节点本身
            if (node.type && (
                node.type.includes('hulue') || 
                node.type.includes('jinyong') || 
                node.type.includes('ALLty') ||
                node.type.includes('Switch') ||
                node.type.includes('GlobalCondition')
            )) {
                return;
            }
            
            switch (action) {
                case "启用":
                    node.mode = LiteGraph.ALWAYS;
                    break;
                case "忽略":
                    node.mode = 4; // BYPASS
                    break;
                case "禁用":
                    node.mode = LiteGraph.NEVER;
                    break;
                default:
                    node.mode = LiteGraph.ALWAYS;
            }
        });
        
        // 保存组状态
        globalConditionState.groupStates.set(group.title, action);
    });
    
    // 刷新画布
    app.graph.setDirtyCanvas(true, true);
}

function handleGlobalConditionControl(node) {
    const widgets = node.widgets;
    if (!widgets) return;
    
    // 获取控制参数
    const enableControl = widgets.find(w => w.name === "enable_control")?.value ?? true;
    const controlMode = widgets.find(w => w.name === "control_mode")?.value ?? "条件控制";
    const targetGroups = widgets.find(w => w.name === "target_groups")?.value ?? "";
    const conditionTrueAction = widgets.find(w => w.name === "condition_true_action")?.value ?? "启用";
    const conditionFalseAction = widgets.find(w => w.name === "condition_false_action")?.value ?? "禁用";
    
    if (!enableControl) {
        console.log("全局条件控制: 控制已禁用");
        return;
    }
    
    // 添加到活跃节点集合
    globalConditionState.activeNodes.add(node.id);
    
    // 解析目标组
    const targetGroupList = parseTargetGroups(targetGroups);
    
    // 模拟条件判断结果（实际应该从节点输出获取）
    // 这里我们监听节点的输出变化
    const conditionResult = node.properties?.lastConditionResult ?? true;
    
    let action;
    switch (controlMode) {
        case "智能控制":
            action = conditionResult ? "启用" : "忽略";
            break;
        case "全部忽略":
            action = "忽略";
            break;
        case "全部禁用":
            action = "禁用";
            break;
        case "全部启用":
            action = "启用";
            break;
        case "条件控制":
            action = conditionResult ? conditionTrueAction : conditionFalseAction;
            break;
        default:
            action = "启用";
    }
    
    // 应用控制
    applyGroupControl(action, targetGroupList);
    
    // 保存状态
    globalConditionState.lastControlMode = controlMode;
    node.properties = node.properties || {};
    node.properties.lastAction = action;
    node.properties.lastTargetGroups = targetGroupList;
}

function createGlobalConditionSettings(node) {
    const dialog = document.createElement("div");
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 20px;
        background-color: #333;
        color: #fff;
        border: 1px solid #ccc;
        z-index: 1000;
        max-height: 80%;
        overflow-y: auto;
        width: 500px;
        border-radius: 8px;
    `;
    
    const title = document.createElement("h3");
    title.textContent = "🌐 全局条件控制设置";
    title.style.marginTop = "0";
    dialog.appendChild(title);
    
    // 当前状态显示
    const statusDiv = document.createElement("div");
    statusDiv.style.cssText = `
        background: #444;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 15px;
    `;
    
    const activeNodesCount = globalConditionState.activeNodes.size;
    const controlledGroupsCount = globalConditionState.groupStates.size;
    
    statusDiv.innerHTML = `
        <strong>当前状态：</strong><br>
        • 活跃控制节点：${activeNodesCount} 个<br>
        • 受控组数量：${controlledGroupsCount} 个<br>
        • 最后控制模式：${globalConditionState.lastControlMode || "无"}
    `;
    dialog.appendChild(statusDiv);
    
    // 组状态显示
    if (globalConditionState.groupStates.size > 0) {
        const groupStatusDiv = document.createElement("div");
        groupStatusDiv.style.cssText = `
            background: #444;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            max-height: 150px;
            overflow-y: auto;
        `;
        
        let groupStatusHtml = "<strong>组控制状态：</strong><br>";
        globalConditionState.groupStates.forEach((action, groupName) => {
            const statusColor = action === "启用" ? "#4CAF50" : 
                              action === "忽略" ? "#FF9800" : "#F44336";
            groupStatusHtml += `<span style="color: ${statusColor}">• ${groupName}: ${action}</span><br>`;
        });
        
        groupStatusDiv.innerHTML = groupStatusHtml;
        dialog.appendChild(groupStatusDiv);
    }
    
    // 快速控制按钮
    const quickControlDiv = document.createElement("div");
    quickControlDiv.innerHTML = "<strong>快速控制：</strong>";
    quickControlDiv.style.marginBottom = "10px";
    dialog.appendChild(quickControlDiv);
    
    const buttonStyle = `
        margin: 5px;
        padding: 8px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    `;
    
    ["全部启用", "全部忽略", "全部禁用"].forEach(action => {
        const btn = document.createElement("button");
        btn.textContent = action;
        btn.style.cssText = buttonStyle + `
            background-color: ${action === "全部启用" ? "#4CAF50" : 
                               action === "全部忽略" ? "#FF9800" : "#F44336"};
            color: white;
        `;
        btn.addEventListener("click", () => {
            const actionMap = {
                "全部启用": "启用",
                "全部忽略": "忽略", 
                "全部禁用": "禁用"
            };
            applyGroupControl(actionMap[action], []);
            document.body.removeChild(dialog);
        });
        quickControlDiv.appendChild(btn);
    });
    
    // 重置按钮
    const resetBtn = document.createElement("button");
    resetBtn.textContent = "重置所有状态";
    resetBtn.style.cssText = buttonStyle + `
        background-color: #607D8B;
        color: white;
        width: 100%;
        margin-top: 10px;
    `;
    resetBtn.addEventListener("click", () => {
        globalConditionState.activeNodes.clear();
        globalConditionState.groupStates.clear();
        globalConditionState.lastControlMode = null;
        applyGroupControl("启用", []);
        document.body.removeChild(dialog);
    });
    dialog.appendChild(resetBtn);
    
    // 关闭按钮
    const closeBtn = document.createElement("button");
    closeBtn.textContent = "关闭";
    closeBtn.style.cssText = buttonStyle + `
        background-color: #666;
        color: white;
        position: absolute;
        top: 10px;
        right: 10px;
    `;
    closeBtn.addEventListener("click", () => {
        document.body.removeChild(dialog);
    });
    dialog.appendChild(closeBtn);
    
    // 作者链接
    const authorBtn = document.createElement("button");
    authorBtn.textContent = "灵仙儿和二狗子";
    authorBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 80px;
        background-color: #ff69b4;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
    `;
    authorBtn.addEventListener("click", () => {
        window.open("https://space.bilibili.com/19723588?spm_id_from=333.1350.jump_directly", "_blank");
    });
    dialog.appendChild(authorBtn);
    
    document.body.appendChild(dialog);
}

// 扩展右键菜单
let originalGetNodeMenuOptions = LGraphCanvas.prototype.getNodeMenuOptions;
LGraphCanvas.prototype.getNodeMenuOptions = function(node) {
    const options = originalGetNodeMenuOptions.apply(this, arguments);
    
    if (node.type === "GlobalConditionControlNode") {
        options.push({
            content: "🌐 全局控制设置",
            callback: () => createGlobalConditionSettings(node)
        });
        
        options.push(null); // 分割线
        
        options.push({
            content: "🔄 立即执行控制",
            callback: () => handleGlobalConditionControl(node)
        });
    }
    
    return options;
};

// 注册扩展
app.registerExtension({
    name: "Comfy.GlobalConditionControl",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "GlobalConditionControlNode") {
            
            // 节点创建时的初始化
            nodeType.prototype.onNodeCreated = function() {
                this.properties = this.properties || {
                    lastConditionResult: true,
                    lastAction: "启用",
                    lastTargetGroups: []
                };
                
                // 监听widget变化
                this.widgets?.forEach(widget => {
                    const originalCallback = widget.callback;
                    widget.callback = (value) => {
                        if (originalCallback) originalCallback(value);
                        
                        // 延迟执行控制，等待所有参数更新
                        setTimeout(() => {
                            handleGlobalConditionControl(this);
                        }, 100);
                    };
                });
            };
            
            // 序列化
            nodeType.prototype.onSerialize = function(info) {
                info.properties = this.properties;
            };
            
            // 反序列化
            nodeType.prototype.onConfigure = function(info) {
                this.properties = info.properties || {
                    lastConditionResult: true,
                    lastAction: "启用", 
                    lastTargetGroups: []
                };
            };
            
            // 节点执行后的回调
            const originalExecute = nodeType.prototype.execute;
            if (originalExecute) {
                nodeType.prototype.execute = function(...args) {
                    const result = originalExecute.apply(this, args);
                    
                    // 获取条件结果并触发控制
                    if (result && result.length >= 2) {
                        this.properties = this.properties || {};
                        this.properties.lastConditionResult = result[1]; // 条件结果
                        handleGlobalConditionControl(this);
                    }
                    
                    return result;
                };
            }
        }
    }
});

// 定期清理无效的节点引用
setInterval(() => {
    const validNodeIds = new Set(app.graph._nodes.map(node => node.id));
    
    // 清理已删除的节点
    globalConditionState.activeNodes.forEach(nodeId => {
        if (!validNodeIds.has(nodeId)) {
            globalConditionState.activeNodes.delete(nodeId);
        }
    });
    
    // 如果没有活跃的控制节点，清理组状态
    if (globalConditionState.activeNodes.size === 0) {
        globalConditionState.groupStates.clear();
        globalConditionState.lastControlMode = null;
    }
}, 5000);

console.log("全局条件控制扩展已加载 🌐🔀"); 