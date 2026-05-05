import json
from collections import deque

class GraphNode:
    def __init__(self, value):
        self.value = value
        self.neighbors = {}  # {neighbor_node: weight}

    def add_neighbor(self, neighbor, weight=1):
        self.neighbors[neighbor] = weight

    def remove_neighbor(self, neighbor):
        if neighbor in self.neighbors:
            del self.neighbors[neighbor]

    def __str__(self):
        return str(self.value)

class Graph:
    def __init__(self):
        self.nodes = {}  # {node_value: GraphNode_object}

    def add_node(self, value):
        if value not in self.nodes:
            self.nodes[value] = GraphNode(value)
            return True
        print(f"Ошибка: Вершина с значением '{value}' уже существует.")
        return False

    def remove_node(self, value):
        if value in self.nodes:
            del self.nodes[value]
            # Удаляем связи с другими вершинами
            for node_value, node in self.nodes.items():
                node.remove_neighbor(self.nodes[value])
            return True
        print(f"Ошибка: Вершина с значением '{value}' не найдена.")
        return False

    def add_edge(self, value1, value2, weight=1):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2]
            node1.add_neighbor(node2, weight)
            return True
        print("Ошибка: Одна или обе вершины не найдены. Невозможно добавить ребро.")
        return False

    def remove_edge(self, value1, value2):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2]
            node1.remove_neighbor(node2)
            return True
        print("Ошибка: Одна или обе вершины не найдены. Невозможно удалить ребро.")
        return False

    def bfs(self, start_value):
        if start_value not in self.nodes:
            print("Ошибка: Стартовая вершина не найдена.")
            return []

        visited = set()
        queue = deque([self.nodes[start_value]])
        result = []

        while queue:
            current_node = queue.popleft()
            if current_node.value not in visited:
                visited.add(current_node.value)
                result.append(current_node.value)
                for neighbor in current_node.neighbors:
                    queue.append(neighbor)
        return result

    def dfs(self, start_value):
        if start_value not in self.nodes:
            print("Ошибка: Стартовая вершина не найдена.")
            return []

        visited = set()
        stack = [self.nodes[start_value]]
        result = []

        while stack:
            current_node = stack.pop()
            if current_node.value not in visited:
                visited.add(current_node.value)
                result.append(current_node.value)
                for neighbor in current_node.neighbors:
                    stack.append(neighbor)
        return result

    def dijkstra(self, start_value, end_value):
        if start_value not in self.nodes or end_value not in self.nodes:
            print("Ошибка: Стартовая или конечная вершина не найдены.")
            return None, float('inf')

        distances = {node_value: float('inf') for node_value in self.nodes}
        distances[start_value] = 0
        previous_nodes = {}

        nodes_to_visit = list(self.nodes.values())

        while nodes_to_visit:
            nodes_to_visit.sort(key=lambda node: distances[node.value])
            current_node = nodes_to_visit.pop(0)

            if current_node.value == end_value:
                path = []
                current = end_value
                while current is not None:
                    path.append(current)
                    current = previous_nodes.get(current)
                return path[::-1], distances[end_value]

            if distances[current_node.value] == float('inf'):
                break

            for neighbor, weight in current_node.neighbors.items():
                distance = distances[current_node.value] + weight
                if distance < distances[neighbor.value]:
                    distances[neighbor.value] = distance
                    previous_nodes[neighbor.value] = current_node.value

        return None, float('inf')

    def save_to_json(self, filename):
        data = {
            "nodes": {},
            "edges": []
        }
        for value, node in self.nodes.items():
            values_neighbors = {}
            for neighbor, weight in node.neighbors.items():
                values_neighbors[neighbor.value] = weight
            data["nodes"][value] = values_neighbors

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Граф сохранен в {filename}")

    def load_from_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.nodes = {}
            for node_value, neighbors_data in data["nodes"].items():
                self.add_node(node_value)

            # После добавления всех узлов, добавляем ребра
            for node_value, neighbors_data in data["nodes"].items():
                for neighbor_value, weight in neighbors_data.items():
                    self.add_edge(node_value, neighbor_value, weight)

            print(f"Граф загружен из {filename}")
        except FileNotFoundError:
            print(f"Ошибка: Файл {filename} не найден.")
        except json.JSONDecodeError:
            print(f"Ошибка: Некорректный формат JSON в файле {filename}.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке графа: {e}")


class GraphFactory:
    def create_graph(self, graph_type="undirected"):
        if graph_type == "directed":
            return DirectedGraph()
        elif graph_type == "weighted":
            return WeightedGraph()
        else: # undirected by default
            return UndirectedGraph()

class DirectedGraph(Graph):
    def add_edge(self, value1, value2, weight=1):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2]
            node1.add_neighbor(node2, weight)
            return True
        print("Ошибка: Одна или обе вершины не найдены. Невозможно добавить ребро.")
        return False

    def remove_edge(self, value1, value2):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2] # Для направленного графа убираем только исходящее ребро
            node1.remove_neighbor(node2)
            return True
        print("Ошибка: Одна или обе вершины не найдены. Невозможно удалить ребро.")
        return False

class UndirectedGraph(Graph):
    def add_edge(self, value1, value2, weight=1):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2]
            node1.add_neighbor(node2, weight)
            node2.add_neighbor(node1, weight) # Для ненаправленного добавляем оба направления
            return True
        print("Ошибка: Одна или обе вершины не найдены. Невозможно добавить ребро.")
        return False

    def remove_edge(self, value1, value2):
        if value1 in self.nodes and value2 in self.nodes:
            node1 = self.nodes[value1]
            node2 = self.nodes[value2]
            node1.remove_neighbor(node2)
            node2.remove_neighbor(node1) # Для ненаправленного удаляем оба направления
            return True
        print("Ошибка: Одна или обе вершины не найдены. Невозможно удалить ребро.")
        return False

class WeightedGraph(Graph): # В данном случае, WeightedGraph наследует от Graph и может быть как направленным, так и ненаправленным.
                           # Для простоты, основные методы add_edge и remove_edge в Graph работают с весами,
                           # поэтому WeightedGraph здесь может не требовать дополнительной логики,
                           # если базовый Graph уже поддерживает веса.
                           # Если нужно строго разделять, то можно переопределить add_edge/remove_edge,
                           # аналогично DirectedGraph/UndirectedGraph, но с учетом весов.
    pass

# --- Пример использования ---
if __name__ == "__main__":
    factory = GraphFactory()

    # Создание ненаправленного графа
    undirected_graph = factory.create_graph("undirected")
    undirected_graph.add_node("A")
    undirected_graph.add_node("B")
    undirected_graph.add_node("C")
    undirected_graph.add_edge("A", "B")
    undirected_graph.add_edge("B", "C")

    print("Ненаправленный граф BFS:", undirected_graph.bfs("A"))
    print("Ненаправленный граф DFS:", undirected_graph.dfs("A"))

    # Сохранение и загрузка ненаправленного графа
    undirected_graph.save_to_json("undirected_graph.json")
    loaded_undirected_graph = factory.create_graph("undirected")
    loaded_undirected_graph.load_from_json("undirected_graph.json")
    print("Загруженный ненаправленный граф BFS:", loaded_undirected_graph.bfs("A"))


    # Создание направленного графа
    directed_graph = factory.create_graph("directed")
    directed_graph.add_node("1")
    directed_graph.add_node("2")
    directed_graph.add_node("3")
    directed_graph.add_edge("1", "2")
    directed_graph.add_edge("2", "3")

    print("\nНаправленный граф BFS:", directed_graph.bfs("1"))
    print("Направленный граф DFS:", directed_graph.dfs("1"))

    # Создание взвешенного графа
    weighted_graph = factory.create_graph("weighted")
    weighted_graph.add_node("X")
    weighted_graph.add_node("Y")
    weighted_graph.add_node("Z")
    weighted_graph.add_edge("X", "Y", 10)
    weighted_graph.add_edge("Y", "Z", 5)
    weighted_graph.add_edge("X", "Z", 15)

    print("\nВзвешенный граф BFS:", weighted_graph.bfs("X"))
    print("Взвешенный граф DFS:", weighted_graph.dfs("X"))

    path, distance = weighted_graph.dijkstra("X", "Z")
    print(f"Кратчайший путь от X до Z (навзвешенный): {path} с весом {distance}")

    # BFS для поиска кратчайшего пути в невзвешенном графе (используем undirected_graph)
    path_bfs = undirected_graph.bfs("A") # BFS сам по себе возвращает порядок обхода,
                                          # для нахождения пути нужно доработать BFS
    print(f"Порядок обхода BFS необработанного двунаправленного графа: {path_bfs}")

    # Пример проверки ввода:
    undirected_graph.add_node("A") # Попытка добавить существующую вершину
    undirected_graph.add_edge("A", "D") # Попытка добавить ребро к несуществующей вершине
