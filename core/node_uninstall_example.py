"""
节点卸载删除示例

本文件演示了如何在Cognot系统中卸载和删除节点的几种方法：
1. 删除单个节点
2. 批量删除节点
3. 临时禁用节点
4. 完全卸载一个模型的所有节点

使用说明：
- 直接运行此文件可查看示例效果
- 可以根据需要修改示例代码以适应实际需求
"""

from core.node_registry import remove_node, get_all_nodes, clear_all_nodes


def example_remove_single_node():
    """示例：删除单个节点"""
    print("\n=== 示例1：删除单个节点 ===")
    
    # 首先查看当前所有节点
    all_nodes = get_all_nodes()
    print(f"当前节点总数：{len(all_nodes)}")
    print(f"节点列表：{list(all_nodes.keys())}")
    
    # 选择一个要删除的节点（这里以假设存在的节点为例）
    node_to_remove = "example_node"  # 替换为实际存在的节点名称
    
    if node_to_remove in all_nodes:
        # 删除节点
        success = remove_node(node_to_remove)
        if success:
            print(f"✓ 成功删除节点：{node_to_remove}")
        else:
            print(f"✗ 删除节点失败：{node_to_remove}")
    else:
        print(f"⚠️  节点 '{node_to_remove}' 不存在")
    
    # 再次查看节点列表
    updated_nodes = get_all_nodes()
    print(f"更新后节点总数：{len(updated_nodes)}")



def example_batch_remove_nodes():
    """示例：批量删除节点"""
    print("\n=== 示例2：批量删除节点 ===")
    
    # 首先查看当前所有节点
    all_nodes = get_all_nodes()
    print(f"当前节点总数：{len(all_nodes)}")
    
    # 选择要删除的节点列表（这里以假设的节点前缀为例）
    nodes_to_remove = []
    prefix_to_remove = "old_"  # 要删除的节点前缀
    
    # 收集所有匹配前缀的节点
    for node_name in all_nodes.keys():
        if node_name.startswith(prefix_to_remove):
            nodes_to_remove.append(node_name)
    
    if nodes_to_remove:
        print(f"找到 {len(nodes_to_remove)} 个以 '{prefix_to_remove}' 开头的节点：")
        for node_name in nodes_to_remove:
            print(f"  - {node_name}")
        
        # 批量删除节点
        print("\n开始批量删除...")
        for node_name in nodes_to_remove:
            success = remove_node(node_name)
            if success:
                print(f"✓ 删除节点：{node_name}")
            else:
                print(f"✗ 删除节点失败：{node_name}")
    else:
        print(f"⚠️  没有找到以 '{prefix_to_remove}' 开头的节点")
    
    # 再次查看节点列表
    updated_nodes = get_all_nodes()
    print(f"\n更新后节点总数：{len(updated_nodes)}")



def example_remove_model_nodes():
    """示例：删除一个模型的所有节点"""
    print("\n=== 示例3：删除一个模型的所有节点 ===")
    
    # 首先查看当前所有节点
    all_nodes = get_all_nodes()
    print(f"当前节点总数：{len(all_nodes)}")
    
    # 选择要删除的模型名称（这里以 "old_model" 为例）
    model_name = "old_model"  # 替换为实际的模型名称
    
    # 收集所有与该模型相关的节点
    model_nodes = []
    for node_name in all_nodes.keys():
        if model_name in node_name:
            model_nodes.append(node_name)
    
    if model_nodes:
        print(f"找到 {len(model_nodes)} 个与 '{model_name}' 相关的节点：")
        for node_name in model_nodes:
            print(f"  - {node_name}")
        
        # 询问是否删除
        print(f"\n确定要删除 '{model_name}' 的所有节点吗？")
        confirm = input("输入 'yes' 确认删除：")
        
        if confirm.lower() == "yes":
            # 批量删除节点
            print("\n开始删除模型节点...")
            for node_name in model_nodes:
                success = remove_node(node_name)
                if success:
                    print(f"✓ 删除节点：{node_name}")
                else:
                    print(f"✗ 删除节点失败：{node_name}")
            
            # 也可以删除模型相关的导入文件（如果需要）
            # import os
            # model_file_path = f"core/{model_name}_nodes.py"
            # if os.path.exists(model_file_path):
            #     os.remove(model_file_path)
            #     print(f"✓ 删除模型文件：{model_file_path}")
    else:
        print(f"⚠️  没有找到与 '{model_name}' 相关的节点")
    
    # 再次查看节点列表
    updated_nodes = get_all_nodes()
    print(f"\n更新后节点总数：{len(updated_nodes)}")



def example_temporary_disable_nodes():
    """示例：临时禁用节点（通过删除并保留重新注册的方式）"""
    print("\n=== 示例4：临时禁用节点 ===")
    
    # 临时禁用节点的最佳做法是：
    # 1. 记录要禁用的节点名称
    # 2. 删除这些节点
    # 3. 当需要重新启用时，重新导入相关模块
    
    nodes_to_disable = ["example_node_1", "example_node_2"]  # 替换为实际节点名称
    
    print(f"要临时禁用的节点：{nodes_to_disable}")
    
    # 禁用（删除）节点
    for node_name in nodes_to_disable:
        success = remove_node(node_name)
        if success:
            print(f"✓ 已禁用节点：{node_name}")
    
    print("\n要重新启用这些节点，只需重新导入包含这些节点的模块：")
    print("例如：")
    print("import importlib")
    print("import core.example_nodes")
    print("importlib.reload(core.example_nodes)")



def example_clear_all_nodes():
    """示例：清除所有节点（谨慎使用）"""
    print("\n=== 示例5：清除所有节点 ===")
    print("警告：此操作将删除所有节点，包括系统默认节点！")
    print("仅在开发和测试环境中使用此功能。")
    
    confirm = input("输入 'yes' 确认清除所有节点：")
    
    if confirm.lower() == "yes":
        # 清除所有节点
        count = clear_all_nodes()
        print(f"✓ 已清除 {count} 个节点")
        print(f"当前节点总数：{len(get_all_nodes())}")
    else:
        print("✗ 操作已取消")



def main():
    """运行所有示例"""
    print("Cognot 节点卸载删除示例")
    print("=" * 50)
    
    # 运行各个示例
    example_remove_single_node()
    example_batch_remove_nodes()
    example_remove_model_nodes()
    example_temporary_disable_nodes()
    
    # 注意：example_clear_all_nodes() 会清除所有节点，包括系统默认节点
    # 仅在需要时取消注释并运行
    # example_clear_all_nodes()
    
    print("\n" + "=" * 50)
    print("所有示例运行完毕")


if __name__ == "__main__":
    main()
