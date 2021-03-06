# -*- coding: utf-8 -*-


class Metric(object):

    def __init__(self, eps=1e-15):
        super(Metric, self).__init__()

        self.eps = eps
        self.total = 0.0
        self.correct_arcs = 0.0
        self.correct_rels = 0.0

    def __repr__(self):
        return f"UAS: {self.uas:.2%} LAS: {self.las:.2%}"

    def __call__(self, pred_arcs, pred_rels, gold_arcs, gold_rels):
        arc_mask = pred_arcs.eq(gold_arcs)
        rel_mask = pred_rels.eq(gold_rels) & arc_mask

        self.total += len(arc_mask)
        self.correct_arcs += arc_mask.sum().item()
        self.correct_rels += rel_mask.sum().item()

    def __lt__(self, other):
        return self.score < other

    def __le__(self, other):
        return self.score <= other

    def __ge__(self, other):
        return self.score >= other

    def __gt__(self, other):
        return self.score > other

    @property
    def score(self):
        return self.las

    @property
    def uas(self):
        if self.total > 0:
            return self.correct_arcs / (self.total)
        else:
            return self.eps
    
    
    @property
    def las(self):
        if self.total > 0:
            return self.correct_rels / (self.total)
        else:
            return self.eps
