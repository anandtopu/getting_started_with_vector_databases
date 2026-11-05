"""Seeded multilayer cosine graph with greedy descent and bounded best-first search."""

import heapq

import numpy as np


class HNSW:
    def __init__(self, matrix, M=8, efConstruction=40, efSearch=32, seed=42):
        if M < 2 or efConstruction < M or efSearch < 1:
            raise ValueError("Require M>=2, efConstruction>=M and positive efSearch")
        self.matrix = matrix
        self.M = M
        self.efSearch = efSearch
        self.layers = []
        self.entry = 0
        rng = np.random.default_rng(seed)
        for row, q in enumerate(matrix):
            level = min(16, int(-np.log(max(rng.random(), 1e-12)) / np.log(M)))
            old_top = len(self.layers) - 1
            while len(self.layers) <= level:
                self.layers.append({})
            for layer in self.layers[: level + 1]:
                layer[row] = []
            if row:
                entry = self.entry
                for height in range(old_top, level, -1):
                    entry = self._beam(q, entry, height, 1)[0]
                for height in range(min(old_top, level), -1, -1):
                    neighbors = self._diverse(q, self._beam(q, entry, height, efConstruction), M)
                    graph = self.layers[height]
                    graph[row] = neighbors
                    for other in neighbors:
                        linked = graph[other] + [row]
                        if len(linked) > M:
                            linked = self._diverse(matrix[other], linked, M)
                        graph[other] = linked
                    entry = neighbors[0]
            if level > old_top:
                self.entry = row
        # Keep each layer reachable. Two of its bounded links form a ring in
        # insertion order; the remaining links provide geometric shortcuts.
        for graph in self.layers:
            nodes = list(graph)
            for pos, node in enumerate(nodes):
                ring = [nodes[(pos - 1) % len(nodes)], nodes[(pos + 1) % len(nodes)]]
                graph[node] = [i for i in dict.fromkeys(ring + graph[node]) if i != node][:M]

    def _diverse(self, query, candidates, limit):
        values = self.matrix[candidates] @ query
        order = np.argsort(-values, kind="stable")
        chosen = []
        skipped = []
        for offset in order:
            node = candidates[offset]
            if not chosen or np.max(self.matrix[chosen] @ self.matrix[node]) < values[offset]:
                chosen.append(node)
                if len(chosen) == limit:
                    break
            else:
                skipped.append(node)
        return (chosen + skipped)[:limit]

    def _beam(self, q, entry, height, width):
        graph = self.layers[height]
        initial = float(self.matrix[entry] @ q)
        frontier = [(-initial, entry)]
        best = [(initial, -entry)]
        seen = {entry}
        while frontier:
            neg, node = heapq.heappop(frontier)
            if len(best) >= width and -neg < best[0][0]:
                break
            neighbors = [i for i in graph[node] if i not in seen]
            seen.update(neighbors)
            if neighbors:
                for i, score in zip(neighbors, (self.matrix[neighbors] @ q).tolist(), strict=True):
                    if len(best) < width or (score, -i) > best[0]:
                        heapq.heappush(frontier, (-score, i))
                        heapq.heappush(best, (score, -i))
                        if len(best) > width:
                            heapq.heappop(best)
        return [-n for _, n in sorted(best, reverse=True)]

    def candidates(self, q, count):
        entry = self.entry
        for h in range(len(self.layers) - 1, 0, -1):
            entry = self._beam(q, entry, h, 1)[0]
        return self._beam(q, entry, 0, max(count, self.efSearch))

    @property
    def payload_bytes(self):
        # Logical 32-bit node IDs and adjacent IDs, excluding Python allocator overhead.
        return sum(4 * (1 + len(edges)) for layer in self.layers for edges in layer.values())

    def filtered_candidates(self, q, count, eligible):
        """Traverse through ineligible bridges while accepting only eligible results."""
        if not eligible:
            return []
        entry = self.entry
        for h in range(len(self.layers) - 1, 0, -1):
            entry = self._beam(q, entry, h, 1)[0]
        queue = [(-float(self.matrix[entry] @ q), entry)]
        visited = {entry}
        accepted = []
        budget = max(self.efSearch, count)
        while queue and len(accepted) < budget:
            neg, row = heapq.heappop(queue)
            if row in eligible:
                accepted.append((neg, row))
            neighbors = [i for i in self.layers[0][row] if i not in visited]
            visited.update(neighbors)
            if neighbors:
                for node, score in zip(neighbors, self.matrix[neighbors] @ q, strict=True):
                    heapq.heappush(queue, (-float(score), node))
        return [row for _, row in sorted(accepted)]
