![灵仙儿和二狗子](docs/LOGO2.png "LOGO2")
哈喽！我是二狗子（2🐕）！这是一套针对Comfyui流程设计师及玩家的混合组开关套件，一键实现控制不同组别的忽略禁用   
Hello! I am Er Gouzi （2🐕）！ This is a mixed group switch kit designed for Comfyui process designers and players, which allows for one click control of ignoring and disabling different groups

## 🐕图标可通过鼠标滚轮（中键）随时拖动！！！🐕The icon can be dragged at any time with the mouse wheel (middle button)！！！
## 安装
Installation

首先，打开命令行终端，然后切换到您的ComfyUI的`custom_nodes`目录：   
Firstly, open the command line terminal and then switch to the 'custom_dodes' directory in your ComfyUI:   

```cd /path/to/your/ComfyUI/custom_nodes```

将/path/to/your/ComfyUI替换为您的ComfyUI项目所在的实际路径。   
Replace/path/to/your/ComfyUI with the actual path where your ComfyUI project is located.   
接下来，克隆ergouzi-kaiguan仓库：   
Next, clone the ergouzi kaiguan repository:   

```git clone https://github.com/11dogzi/Comfyui-ergouzi-kaiguan.git```

## 更新日志    
Update log    

🌐 **2025/1/2 新增全局组条件控制节点**     
2025/1/2 Added Global Group Condition Control Node    
根据条件判断自动控制ComfyUI节点组的开关状态（启用/禁用/屏蔽）    
Automatically control the on/off status of ComfyUI node groups based on conditional judgment (enable/disable/bypass)    

• 全局组条件控制🌐🔀 - 智能条件判断+组控制    
• 智能组开关🎯 - 简化的组开关控制    
• 支持8种比较类型和复杂条件逻辑    
• 可视化控制面板和状态管理    

2025/2/20修正连线组开关ture为启用/flase为禁用     
On May 2, 2023, the wiring group switch 'ture' was enabled and 'flash' was disabled    
2024/12/09新增桌宠编辑器    
2024/12/09 Added Table Pet Editor       
在执行任务时播放自定义gif动画     
Play custom GIF animations during task execution     
![灵仙儿和二狗子](docs/桌宠编辑器1.png "桌宠编辑器1")  
![灵仙儿和二狗子](docs/桌宠编辑器2.png "桌宠编辑器2")  
![灵仙儿和二狗子](docs/桌宠编辑器3.png "桌宠编辑器3")  
Update log
2024/10/20新增任务管理器节点     
New Task Manager Node Added on October 20, 2024    
节点式输入需要执行的任务数量进行执行或取消，实时刷新当前任务数量与完成数量     
Node based input is used to execute or cancel the number of tasks that need to be executed, and the current task count and completion count are refreshed in real-time    
![灵仙儿和二狗子](docs/任务管理器.png "任务管理器")     

任务进行中动画小狗（小狗可以通过长按鼠标滚轮进行拖动Puppies can be dragged by long pressing the mouse wheel）        
(如果你不需要这个功能可以删除Comfyui-ergouzi-kaiguan\web中的kaiguanj.js文件\如果你使用的是2025年2月2日前的版本，还需要删除Comfyui\web\extensions\EG_KG)     
If you don't need this feature, you can delete the kaiguanj.js file in Comfyui-ergouzi-kaiguan\web\kaiguanj.js. If you are using a version before February 2, 2025, you also need to remove Comfyui\web\extensions\EG_KG    
Task in progress animated puppy    
![灵仙儿和二狗子](docs/任务进行动画.png "任务进行动画")      

可以点击声音设置进行任务完成提示音设置    
You can click on the sound settings to set the task completion prompt sound    
![灵仙儿和二狗子](docs/声音设置.png "声音设置")      

## 视频使用教程    
Video usage tutorial    
[视频使用教程][开关节点使用视频教程](https://www.bilibili.com/video/BV1bT421677t/?vd_source=ab266c754171024c866a35bf8097094e)      

## 节点介绍
Node Introduction
## 通用开关节点："Universal switch▶️"    
通过节点右键菜单选项卡进行开关设置，对全局的节点组进行开关方案的勾选，多个"Universal switch▶️"节点建立时，将会每次仅打开的节点生效，防止开关冲突   
Set the switch through the right-click menu tab of the node, select the switch scheme for the global node group, and use multiple"Universal switch▶️"options When a node is established, only the opened nodes will take effect each time to prevent switch conflicts    
![灵仙儿和二狗子](docs/全局开关.png "全局开关")    
![灵仙儿和二狗子](docs/全局开关1.png "全局开关1")    

## 连线开关节点："All Ignore👁️‍🗨️▶️"    
当该节点连接"ALL🚫👁️‍🗨️"时，则对当前节点连接的"ALL🚫👁️‍🗨️"所在组进行忽略处理，可连接多个"ALL🚫👁️‍🗨️"控制多组    
When the node is connected to"ALL🚫👁️‍🗨️"When, the"ALL🚫👁️‍🗨️"connected to the current node"ALL🚫👁️‍🗨️"Ignore the group and connect multiple"ALL🚫👁️‍🗨️"Control multiple groups    
![灵仙儿和二狗子](docs/连线忽略.png "连线忽略")       

## 连线开关节点："All Disable🚫"    
当该节点连接"ALL🚫👁️‍🗨️"时，则对当前节点连接的"ALL🚫👁️‍🗨️"所在组进行禁用处理，可连接多个"ALL🚫👁️‍🗨️"控制多组    
When the node is connected to"ALL🚫👁️‍🗨️"When, the"ALL🚫👁️‍🗨️"connected to the current node"ALL🚫👁️‍🗨️"Disable the group to which you belong, multiple"ALL🚫👁️‍🗨️"connections can be made"ALL🚫👁️‍🗨️"Control multiple groups    
![灵仙儿和二狗子](docs/连线禁用.png "连线禁用")    

## 连线混合开关节点："Hybrid switch🔃"    
当该节点连接"hulue🔃"时，则对当前节点连接的"hulue🔃"所在组进行忽略处理，当该节点连接"jin yong🔃"时，则对当前节点连接的"jin yong🔃"所在组进行禁用处理，可连接多个"jin yong🔃"或者"hulue🔃"进行混合控制    
When the node is connected to"hulue🔃"，The "hulue🔃" of the current node connection Ignore the group you belong to，When the node connects to"jin yong🔃"，The"jin yong🔃"connected to the current node Disable the group in which it belongs，Can connect multiple "jin yong🔃" Or "hulue🔃" Perform mixed control
![灵仙儿和二狗子](docs/连线混合.png "连线混合")     

## 开关点示例： 
Example of switch points    
![灵仙儿和二狗子](docs/开关点.png "开关点")   

## 开关名称设置：    
Switch name setting    
![灵仙儿和二狗子](docs/连线式开关.png "连线式开关")    
![灵仙儿和二狗子](docs/开关名称修改.png "开关名称修改")    

## 功能节点："Recursive switching🔀"    
输入N个输入，对第一个非空值进行输出，可以设置需要切换的输入数量以及记录每个输入点名称    
Input N inputs and output the first non null value. You can set the number of inputs to switch and record the name of each input point
![灵仙儿和二狗子](docs/任意切换.png "任意切换")    
![灵仙儿和二狗子](docs/任意切换1.png "任意切换1")    
![灵仙儿和二狗子](docs/任意切换3.png "任意切换3")    


## 更多SD免费教程
More SD free tutorials   
灵仙儿和二狗子的Bilibili空间，欢迎访问：   
Bilibili space for Lingxian'er and Ergouzi, welcome to visit:   
[灵仙儿二狗子的Bilibili空间](https://space.bilibili.com/19723588?spm_id_from=333.1007.0.0)   
欢迎加入我们的QQ频道，点击这里进入：   
Welcome to our QQ channel, click here to enter:   
[二狗子的QQ频道](https://pd.qq.com/s/3d9ys5wpr)   
![LOGO](docs/LOGO1.png "LOGO1")![LOGO](docs/LOGO1.png "LOGO1")![LOGO](docs/LOGO1.png "LOGO1") 


















