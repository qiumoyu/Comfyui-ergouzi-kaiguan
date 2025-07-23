import os
import sys
import importlib

python = sys.executable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Comfyui-ergouzi-kaiguan", "web")
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def load_nodes():
    for filename in os.listdir(CURRENT_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f".{module_name}", package=__name__)
                if hasattr(module, "NODE_CLASS_MAPPINGS"):
                    NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
                if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
                    NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
                    
                # 特别输出全局条件控制节点的加载信息
                if module_name == "kaiguan_global_condition":
                    print("🌐 全局条件控制节点已成功加载！")
                    print("   - 全局条件控制🌐🔀")
                    print("   - 条件组控制🎯")
                    
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")

load_nodes()

print(f"二狗子开关套件加载完成！共加载 {len(NODE_CLASS_MAPPINGS)} 个节点")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
