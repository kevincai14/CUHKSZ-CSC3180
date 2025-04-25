import configparser
import os
import random
import numpy as np
import math
Flag = True

# ================ 配置加载部分 ================

def load_learning_config():
    """加载 Q-learning 配置"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '../config/q_learning.ini')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在：{config_path}")
    
    # 修改此处，明确指定编码格式
    with open(config_path, 'r', encoding='utf-8') as f:
        config.read_file(f)  # 使用read_file替代read
    
    return {
        'alpha': float(config['learning_parameters']['alpha']),
        'gamma': float(config['learning_parameters']['gamma']),
        'epsilon': float(config['learning_parameters']['epsilon']),
        'episodes': int(config['learning_parameters']['episodes'])
    }

# 加载配置参数
params = load_learning_config()
if not Flag:
    print("配置文件加载失败，使用默认参数")
    alpha = 0.3
    gamma = 0.95
    epsilon = 0.5
    episodes = 2000
else:
    alpha = params['alpha']
    gamma = params['gamma']
    epsilon = params['epsilon']
    episodes = params['episodes']

def read_node_data(filename):
    nodes = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 3:
                print("Invalid node line:", line)
                continue
            node_id, lat, lon = int(parts[0]), float(parts[1]), float(parts[2])
            nodes[node_id] = (lat, lon)
    return nodes


def read_edge_data(filename, nodes):
    """
    读取边数据，使用节点坐标计算欧几里得距离作为边长度
    :param filename: 边数据文件路径
    :param nodes: 从read_node_data()返回的节点字典 {id: (lat, lon)}
    :return: 图结构 {start: {end: distance}}
    """
    graph = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 4:  # 现在只需要edge_id, start, end
                print("Invalid edge line:", line)
                continue

            edge_id, start, end ,correction= int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3])

            # 检查节点是否存在
            if start not in nodes or end not in nodes:
                print(f"Missing node coordinates for edge {edge_id}: {start}->{end}")
                continue

            # 获取节点坐标（经纬度）
            lat1, lon1 = nodes[start]
            lat2, lon2 = nodes[end]

            # 计算欧几里得距离（简单差值）
            # 注意：这不是真实地理距离，只是经纬度的算术差值
            distance = math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)
            distance *= 0.0048476868753
            distance += correction
            # 构建图结构（无向图）
            graph.setdefault(start, {})[end] = distance
            graph.setdefault(end, {})[start] = distance

    return graph


# 初始化 Q 表
def initialize_Q(graph):
    return {state: {action: 0.0 for action in graph[state]} for state in graph}

# ε-贪婪策略
def epsilon_greedy(state, graph, Q):
    if random.uniform(0, 1) < epsilon:
        return random.choice(list(graph[state].keys()))
    else:
        return max(Q[state], key=Q[state].get)

# Q-learning算法
def q_learning(graph, start, goal):
    Q = initialize_Q(graph)
    for episode in range(episodes):
        state = start
        visited = set()
        while state != goal:
            visited.add(state)
            if state not in graph or not graph[state]:
                break  # 死点

            action = epsilon_greedy(state, graph, Q)
            next_state = action
            # 原始奖励
            reward = -graph[state][action]

            # 如果已访问该节点，加惩罚
            if next_state in visited:
                reward -= 10  # 惩罚值，你可以调大惩罚程度

            # Q-learning 更新
            max_q_next = max(Q[next_state].values()) if Q[next_state] else 0
            Q[state][action] += alpha * (reward + gamma * max_q_next - Q[state][action])

            state = next_state
    return Q


def extract_path(Q, start, goal):
    state = start
    path = [state]
    visited = set()
    while state != goal:
        visited.add(state)
        if state not in Q or not Q[state]:
            print(f"在节点 {state} 停止：没有可选动作。")
            return path
        action = max(Q[state], key=Q[state].get)
        if action in visited:
            print(f"检测到循环路径，停在 {action}")
            return path
        path.append(action)
        state = action
    return path

# test主程序
if __name__ == "__main__":
    nodes = read_node_data(r"data\node_py_data.txt")  # 节点数据文件
    graph = read_edge_data(r"data\edge_py_data.txt")   # 边数据文件

    # 显示邻接表
    print("邻接表:")
    for node, neighbors in graph.items():
        print(f"{node} -> {neighbors}")

    start_node = int(input("输入起点节点ID："))
    goal_node = int(input("输入终点节点ID："))


    Q = q_learning(graph, start_node, goal_node)

    #     # 打印 Q 表
    # print("\nQ 表：")
    # for state in sorted(Q.keys()):
    #     print(f"从节点 {state} 出发：")
    #     for action in Q[state]:
    #         print(f"  到 {action} 的 Q 值：{Q[state][action]:.2f}")

    path = extract_path(Q, start_node, goal_node)
    print(f"\n从节点 {start_node} 到节点 {goal_node} 的路径：{path}")
