# -*- coding: utf-8 -*-

from nodebox.graphics import *
from nodebox.graphics.physics import Node, Edge, Graph
from ..helpers import calculate_column_density, calculate_row_density


class KeywordGraphGUI():
    """Draw and interact with the graph.
    """
    def __init__(self, title):
        self.edges_data = {}
        self.nodes = []
        self.canvas = Canvas(width=1000, height=600, name=title, resizable=True)
        self.g = Graph()
        self.selected_node = None
        self.clicked = None
        self.translate_x = 500
        self.translate_y = 300
        self.dragging = False
        self.ctrl_pressed = False
        self.first_node = None
        self.selected_edge = None

    def add_node(self, name, root=False):
        if name in self.nodes:
            return
        self.nodes.append(name)
        self.g.add_node(id=name, radius=10, root=root, fill=Color(1, 0.7, 0.0, 1), fontsize=12)

    def add_edge(self, n1, n2, data=None, stroke=Color(0, 0, 0, 0.3), strokewidth=2, *args, **kwargs):
        self.add_node(n1)
        self.add_node(n2)
        self.edges_data[(n1, n2)] = data
        self.g.add_edge(n1, n2, stroke=stroke, strokewidth=strokewidth, *args, **kwargs)

    def _draw(self):
        canvas.clear()
        background(1)
        translate(self.translate_x, self.translate_y)

        # With directed=True, edges have an arrowhead indicating the direction of the connection.
        # With weighted=True, Node.centrality is indicated by a shadow under high-traffic nodes.
        # With weighted=0.0-1.0, indicates nodes whose centrality > the given threshold.
        # This requires some extra calculations.
        self.g.draw(weighted=0.5, directed=True)
        # self.g.update(iterations=10)

        dx = self.canvas.mouse.x - self.translate_x  # Undo translate()
        dy = self.canvas.mouse.y - self.translate_y

        if self.canvas.mouse.pressed and self.selected_node is None:
            current_node = self.g.node_at(dx, dy)
            if self.canvas.mouse.dragged and current_node is not None:
                self.selected_node = current_node

            if current_node is None and self.canvas.mouse.dragged:
                delta_x = self.canvas.mouse.dx
                delta_y = self.canvas.mouse.dy
                # if delta_x > 1 or delta_y > 1:
                self.translate_x += delta_x
                self.translate_y += delta_y

            if current_node is not None and not self.canvas.mouse.dragged and self.ctrl_pressed:
                if self.first_node is None:
                    self.first_node = current_node
                elif current_node.id != self.first_node.id:
                    edge = self.g.edge(self.first_node.id, current_node.id)
                    if edge is None:
                        edge = self.g.edge(current_node.id, self.first_node.id)
                    if edge is not None:
                        if self.selected_edge is not None:
                            self.selected_edge.stroke = (0, 0, 0, 0.3)
                        self.selected_edge = edge
                        self.selected_edge.stroke = Color(1, 0, 0, 0.6)

        if not self.canvas.mouse.pressed:
            self.selected_node = None
            self.dragging = False

            # check hover
            hovering_node = self.g.node_at(dx, dy)

            if hovering_node is not None and not self.ctrl_pressed and self.selected_edge is not None:
                node_id = hovering_node.id
                if self.selected_edge.node1.id == node_id or self.selected_edge.node2.id == node_id:
                    edge = (self.selected_edge.node1.id, self.selected_edge.node2.id)
                    if self.selected_edge.node1.id == node_id:
                        data = self.edges_data[edge][0]
                    else:
                        data = self.edges_data[edge][1]

                    push()
                    self._draw_node_data(hovering_node, data)
                    pop()

        if self.selected_node is not None:
            self.selected_node.x = dx
            self.selected_node.y = dy

    def _draw_node_data(self, node, data):
        lines = [Text(t, width=300, fontname="Droid Sans Mono") for t in data if len(t) < 30]
        if len(lines) <= 0:
            return
        lines = lines[:20]
        cur_height = 0.0
        for l in lines:
            cur_height += textheight(l) + 5
        box_width = 300
        box_height = cur_height
        box = rect(node.x - box_width - 5, node.y - box_height - 5, box_width + 5, box_height + 5,
                   fill=Color(0.8, 0.8, 0.8, 1))

        cur_height = 0.0
        for l in lines:
            cur_height += textheight(l) + 5
            l.draw(node.x - 300, node.y - cur_height)

    def _on_key_press(self, keys):
        if keys.pressed and (keys.char is None or keys.char == ''):
            if keys.modifiers is not None and len(keys.modifiers) > 0 and keys.modifiers[0] == 'ctrl':
                self.ctrl_pressed = True

    def _on_key_release(self, keys):
        if keys.char is None or keys.char == '':
            if keys.modifiers is not None and len(keys.modifiers) > 0 and keys.modifiers[0] == 'ctrl':
                self.ctrl_pressed = False
                self.first_node = None

    def start(self, iterations=70, distance=30, force=0.01, repulsion_radius=30):
        """Starts the GUI
        """
        self.g.distance = distance   # Overall spacing between nodes.
        self.g.layout.force = force  # Strength of the attractive & repulsive force.
        self.g.layout.repulsion = repulsion_radius   # Repulsion radius.
        self.g.update(iterations=iterations)
        self.canvas.on_key_press = self._on_key_press
        self.canvas.on_key_release = self._on_key_release
        self.canvas.draw = self._draw
        self.canvas.run()


def draw_keyword_biclusters(edges):
    graph = KeywordGraphGUI('Keyphrase biclusters graph')
    for (kw1, kw2), (num, data1, data2, g_val) in edges.iteritems():
        graph.add_edge(kw1, kw2, (data1, data2), weight=3.1 - 3.0 / num, stroke=Color(0, 0, 0, 0.3))
    graph.start()


def construct_keyword_graph(keyword_biclusters, bicluster_num=50):
    kw_edges = {}
    keyword_biclusters = keyword_biclusters[:bicluster_num]
    for keyword_bicluster in keyword_biclusters:
        # if keyword_bicluster.g_value < 1.0:
        #     break

        # find dominating column
        max_column = -1
        max_col_density = -1000
        for i, kw in enumerate(keyword_bicluster.keyword_columns):
            col_density = calculate_column_density(i, keyword_bicluster.similarity_matrix)
            if col_density > max_col_density:
                max_col_density = col_density
                max_column = kw

        # find dominating row
        max_row = -1
        max_row_density = -1000
        for i, kw in enumerate(keyword_bicluster.keyword_rows):
            row_density = calculate_row_density(i, keyword_bicluster.similarity_matrix)
            if row_density > max_row_density:
                max_row_density = row_density
                max_row = kw

        if max_column == max_row:
            print 'self-link for %s' % max_row  # TODO: note printing here and below
            continue

        print '%s -> %s' % (max_column, max_row)
        kw_edge = (max_column, max_row)
        if kw_edge in kw_edges:
            val = kw_edges[kw_edge]
            prev_g_val = val[3]
            if prev_g_val >= keyword_bicluster.g_value:
                kw_edges[kw_edge] = (val[0] + 1, val[1], val[2], prev_g_val)
            else:
                kw_edges[kw_edge] = (val[0] + 1, keyword_bicluster.keyword_columns, keyword_bicluster.keyword_rows,
                                     keyword_bicluster.g_value)
        else:
            kw_edges[kw_edge] = (1, keyword_bicluster.keyword_columns, keyword_bicluster.keyword_rows,
                                 keyword_bicluster.g_value)

    return kw_edges

# for testing purposes
if __name__ == '__main__':
    gui = KeywordGraphGUI('Biclustering graph')
    keywords = ['cluster analysis', 'principal component analysis']
    edges = [('cluster analysis', 'principal component analysis',
              (['1', '2', 'social network visualization'], ['1', '2', 'real_val']))]
    for edge in edges:
        gui.add_edge(edge[0], edge[1], edge[2])

    gui.start()