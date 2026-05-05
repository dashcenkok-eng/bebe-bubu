import json
from collections import deque

class GraphNode:
    """Представляет вершину графа."""
    def __init__(self, value):
        if not isinstance(value, (int, str)):
            raise TypeError("Значение вершины должно быть целым числом или строкой.")
        self.value = value
        self.edges = {}  # Словарь для хранения связей {сосед: вес}

    def add_edge(self, neighbor, weight=1):
        """Добавляет ребро к соседней вершине."""
        if not isinstance(neighbor, GraphNode):
            raise TypeError("Сосед должен быть объектом GraphNode.")
        if not isinstance(weight, (int, float)):
            raise TypeError("Вес ребра должен быть числом.")
        if weight < 0:
            raise ValueError("Вес ребра не может быть отрицательным.")
        self.edges[neighbor] = weight

    def remove_edge(self, neighbor):
        """Удаляет ребро к соседней вершине."""
        if neighbor in self.edges:
            del self.edges[neighbor]

    def __repr__(self):
        return f"Node({self.value})"

class Graph:
    """Базовый класс для представления графа."""
    def __init__(self):
        self.nodes = {}  # Словарь для хранения вершин {значение: объект GraphNode}

    def add_node(self, value):
        """Добавляет вершину в граф."""
        if value in self.nodes:
            raise ValueError(f"Вершина '{value}' уже существует.")
        self.nodes[value] = GraphNode(value)
        return self.nodes[value]

    def get_node(self, value):
        """Возвращает вершину по ее значению."""
        return self.nodes.get(value)

    def remove_node(self, value):
        """Удаляет вершину из графа."""
        if value not in self.nodes:
            return
        node_to_remove = self.nodes[value]
        for node in self.nodes.values():
            node.remove_edge(node_to_remove)
        del self.nodes[value]

    def add_edge(self, value1, value2, weight=1):
        """Добавляет ребро между двумя вершинами."""
        node1 = self.get_node(value1)
        node2 = self.get_node(value2)
        if not node1 or not node2:
            raise ValueError("Одна или обе вершины не существуют.")
        node1.add_edge(node2, weight)

    def remove_edge(self, value1, value2):
        """Удаляет ребро между двумя вершинами."""
        node1 = self.get_node(value1)
        node2 = self.get_node(value2)
        if node1 and node2:
            node1.remove_edge(node2)

    def __repr__(self):
        return f"Graph({list(self.nodes.keys())})"

    def save_to_json(self, filename):
        """Сохраняет граф в JSON файл."""
        graph_data = {
            "nodes": [node.value for node in self.nodes.values()],
            "edges": []
        }
        for node_value, node in self.nodes.items():
            for neighbor, weight in node.edges.items():
                graph_data["edges"].append({
                    "from": node_value,
                    "to": neighbor.value,
                    "weight": weight
                })
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=4)

    def load_from_json(self, filename):
        """Загружает граф из JSON файла."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
        except FileNotFoundError:
            print(f"Файл '{filename}' не найден.")
            return

        self.nodes = {}
        for node_value in graph_data.get("nodes", []):
            self.add_node(node_value)

        for edge in graph_data.get("edges", []):
            from_node_val = edge.get("from")
            to_node_val = edge.get("to")
            weight = edge.get("weight", 1)
            if from_node_val is not None and to_node_val is not None:
                try:
                    self.add_edge(from_node_val, to_node_val, weight)
                except ValueError as e:
                    print(f"Ошибка при добавлении ребра: {e}")

class DirectedGraph(Graph):
    """Направленный граф."""
    def add_edge(self, value1, value2, weight=1):
        """Добавляет направленное ребро."""
        super().add_edge(value1, value2, weight)

class UndirectedGraph(Graph):
    """Ненаправленный граф."""
    def add_edge(self, value1, value2, weight=1):
        """Добавляет ненаправленное ребро (в обе стороны)."""
        super().add_edge(value1, value2, weight)
        super().add_edge(value2, value1, weight)

class WeightedGraph(Graph):
    """Взвешенный граф (может быть направленным или ненаправленным)."""
    def __init__(self):
        super().__init__()

class GraphFactory:
    """Фабрика для создания различных типов графов."""
    @staticmethod
    def create_graph(graph_type="undirected"):
        """Создает граф указанного типа."""
        if graph_type == "directed":
            return DirectedGraph()
        elif graph_type == "undirected":
            return UndirectedGraph()
        elif graph_type == "weighted_directed":
            graph = DirectedGraph()
            graph.is_weighted = True # Добавляем флаг для определения взвешенности
            return graph
        elif graph_type == "weighted_undirected":
            graph = UndirectedGraph()
            graph.is_weighted = True
            return graph
        else:
            raise ValueError(f"Неизвестный тип графа: {graph_type}")

class GraphNavigator:
    """Приложение для навигации по графам."""
    def __init__(self):
        self.graph = None

    def create_graph(self, graph_type="undirected"):
        """Создает новый граф с помощью фабрики."""
        self.graph = GraphFactory.create_graph(graph_type)
        print(f"Создан '{graph_type}' граф.")

    def load_graph(self, filename):
        """Загружает граф из JSON файла."""
        if not self.graph:
            # Попытаться угадать тип графа на основе данных JSON
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Простая эвристика: если есть хоть одно ребро с весом, считаем взвешенным
                is_weighted = any(edge.get("weight", 1) != 1 for edge in data.get("edges", []))
                # Попробуем определить направленность, если возможно
                is_directed = False
                if data.get("edges"):
                    edges_set = set((e.get("from"), e.get("to")) for e in data.get("edges"))
                    for edge in data.get("edges"):
                        if (edge.get("to"), edge.get("from")) in edges_set and edge.get("from") != edge.get("to"):
                            is_directed = False # Если есть обратное ребро, скорее всего ненаправленный
                            break
                        is_directed = True # Иначе считаем направленным по умолчанию

                graph_type = ""
                if is_weighted:
                    graph_type = "weighted_"
                graph_type += "directed" if is_directed else "undirected"

                self.graph = GraphFactory.create_graph(graph_type)
            except (FileNotFoundError, json.JSONDecodeError):
                print("Не удалось определить тип графа. Пожалуйста, укажите явно.")
                return
        self.graph.load_from_json(filename)
        print(f"Граф загружен из '{filename}'.")

    def save_graph(self, filename):
        """Сохраняет текущий граф в JSON файл."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        self.graph.save_to_json(filename)
        print(f"Граф сохранен в '{filename}'.")

    def add_node(self, value):
        """Добавляет вершину в текущий граф."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        try:
            self.graph.add_node(value)
            print(f"Вершина '{value}' добавлена.")
        except ValueError as e:
            print(f"Ошибка: {e}")

    def add_edge(self, value1, value2, weight_str="1"):
        """Добавляет ребро между двумя вершинами."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        try:
            weight = int(weight_str) if hasattr(self.graph, 'is_weighted') and self.graph.is_weighted else 1
            self.graph.add_edge(value1, value2, weight)
            print(f"Ребро между '{value1}' и '{value2}' добавлено (вес: {weight}).")
        except (ValueError, TypeError) as e:
            print(f"Ошибка при добавлении ребра: {e}")

    def remove_node(self, value):
        """Удаляет вершину из текущего графа."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        self.graph.remove_node(value)
        print(f"Вершина '{value}' и связанные ребра удалены.")

    def remove_edge(self, value1, value2):
        """Удаляет ребро между двумя вершинами."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        self.graph.remove_edge(value1, value2)
        print(f"Ребро между '{value1}' и '{value2}' удалено.")

    def bfs(self, start_value):
        """Выполняет обход в ширину."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        start_node = self.graph.get_node(start_value)
        if not start_node:
            print(f"Вершина '{start_value}' не найдена.")
            return

        visited = set()
        queue = deque([start_node])
        result = []

        while queue:
            current_node = queue.popleft()
            if current_node.value not in visited:
                visited.add(current_node.value)
                result.append(current_node.value)
                for neighbor in current_node.edges:
                    if neighbor.value not in visited:
                        queue.append(neighbor)
        print(f"BFS (от '{start_value}'): {result}")

    def dfs(self, start_value):
        """Выполняет обход в глубину."""
        if not self.graph:
            print("Сначала создайте или загрузите граф.")
            return
        start_node = self.graph.get_node(start_value)
        if not start_node:
            print(f"Вершина '{start_value}' не найдена.")
            return

        visited = set()
        stack = [start_node]
        result = []

        while stack:
            current_node = stack.pop()
            if current_node.value not in visited:
                visited.add(current_node.value)
                result.append(current_node.value)
                for neighbor in current_node.edges:
                    if neighbor.value not in visited:
                        stack.append(neighbor)
        print(f"DFS (от '{start_value}'): {result}")

    def dijkstra(self, start_value, end_value):
        """Находит кратчайший путь с помощью алгоритма Дейкстры."""
        if not self.graph or not hasattr(self.graph, 'is_weighted') or not self.graph.is_weighted:
            print("Граф не является взвешенным или не создан. Используйте BFS для невзвешенных графов.")
            return

        start_node = self.graph.get_node(start_value)
        end_node = self.graph.get_node(end_value)
        if not start_node or not end_node:
            print("Одна или обе вершины не найдены.")
            return

        distances = {node.value: float('inf') for node in self.graph.nodes.values()}
        distances[start_value] = 0
        predecessors = {node.value: None for node in self.graph.nodes.values()}
        unvisited = set(self.graph.nodes.values())

        while unvisited:
            current_node = min(unvisited, key=lambda node: distances[node.value])
            unvisited.remove(current_node)

            if current_node == end_node:
                break

            for neighbor, weight in current_node.edges.items():
                distance = distances[current_node.value] + weight
                if distance < distances[neighbor.value]:
                    distances[neighbor.value] = distance
                    predecessors[neighbor.value] = current_node.value

        path = []
        current = end_value
        while current is not None:
            path.insert(0, current)
            current = predecessors[current]

        if distances[end_value] == float('inf'):
            print(f"Путь от '{start_value}' до '{end_value}' не найден.")
        else:
            print(f"Кратчайший путь (Дейкстра) от '{start_value}' до '{end_value}': {path} (длина: {distances[end_value]})")

    def shortest_path_bfs(self, start_value, end_value):
        """Находит кратчайший путь для невзвешенных графов с помощью BFS."""
        if not self.graph or (hasattr(self.graph, 'is_weighted') and self.graph.is_weighted):
            print("Граф взвешен или не создан. Используйте Дейкстру для взвешенных графов.")
            return

        start_node = self.graph.get_node(start_value)
        end_node = self.graph.get_node(end_value)
        if not start_node or not end_node:
            print("Одна или обе вершины не найдены.")
            return

        queue = deque([(start_node, [start_node.value])])
        visited = {start_node.value}

        while queue:
            current_node, path = queue.popleft()

            if current_node == end_node:
                print(f"Кратчайший путь (BFS) от '{start_value}' до '{end_value}': {path}")
                return

            for neighbor in current_node.edges:
                if neighbor.value not in visited:
                    visited.add(neighbor.value)
                    new_path = path + [neighbor.value]
                    queue.append((neighbor, new_path))

        print(f"Путь от '{start_value}' до '{end_value}' не найден.")


# --- Пример использования ---
if __name__ == "__main__":
    navigator = GraphNavigator()

    # Создание графа
    navigator.create_graph("weighted_undirected") # Создаем взвешенный ненаправленный граф

    # Добавление вершин
    navigator.add_node("A")
    navigator.add_node("B")
    navigator.add_node("C")
    navigator.add_node("D")
    navigator.add_node("E")

    # Добавление ребер
    navigator.add_edge("A", "B", "5")
    navigator.add_edge("A", "C", "3")
    navigator.add_edge("B", "D", "2")
    navigator.add_edge("C", "D", "7")
    navigator.add_edge("D", "E", "4")
    navigator.add_edge("A", "E", "10") # Добавим еще одно ребро

    # Обходы графа
    navigator.bfs("A")
    navigator.dfs("A")

    # Поиск кратчайшего пути
    navigator.dijkstra("A", "E")
    navigator.dijkstra("A", "D")

    # Сохранение и загрузка графа
    navigator.save_graph("my_graph.json")

    # Создаем новый навигатор для демонстрации загрузки
    new_navigator = GraphNavigator()
    new_navigator.load_graph("my_graph.json")
    new_navigator.bfs("A")
    new_navigator.dijkstra("A", "E")

    # Демонстрация невзвешенного графа
    print("\n--- Демонстрация невзвешенного графа ---")
    navigator_unweighted = GraphNavigator()
    navigator_unweighted.create_graph("undirected")
    navigator_unweighted.add_node(1)
    navigator_unweighted.add_node(2)
    navigator_unweighted.add_node(3)
    navigator_unweighted.add_edge(1, 2)
    navigator_unweighted.add_edge(2, 3)
    navigator_unweighted.shortest_path_bfs(1, 3)

#
