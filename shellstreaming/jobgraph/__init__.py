# -*- coding: utf-8 -*-
"""
    shellstreaming.jobgraph
    ~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides job graph
"""
import networkx as nx


class JobGraph(nx.DiGraph):
    """Provides utility functions in addition to :class:`networkx.DiGraph`"""

    def begin_nodes(self):
        """Return nodes who don't have incomming edges.

        **Examples**

        .. code-block:: python
            >>> G = JobGraph()
            >>> G.add_path([0,1,2])
            >>> G.begin_nodes()
            [0]
            >>> G.add_edge(3, 1)
            >>> G.begin_nodes()
            [0, 3]
        """
        return [n for n in self.nodes() if self.in_edges(n) == []]

    def end_nodes(self):
        """Return nodes who don't have outcomming edges.

        **Examples**

        .. code-block:: python
            >>> G = JobGraph()
            >>> G.add_path([0,1,2])
            >>> G.end_nodes()
            [2]
            >>> G.add_edge(1, 3)
            >>> G.end_nodes()
            [2, 3]
        """
        return [n for n in self.nodes() if self.out_edges(n) == []]