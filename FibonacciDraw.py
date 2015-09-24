#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import FibonacciHeap
import random
from collections import deque
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class FibonacciTreeView(QWidget):
    def __init__(self, parent=None):
        super(FibonacciTreeView, self).__init__(parent)
        self.heap = None

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_heap(qp)
        qp.end()
        
    def draw_heap(self, qp, margin=20, width=50, height=15):
        qp.setPen(QPen(Qt.red, 2, Qt.SolidLine, Qt.RoundCap))
        size = self.size()

        tree = self.level_traversal()

        levels = len(tree)
        usable_height = size.height()-2*margin-height
        usable_width = size.width()-2*margin-width
        level_height = usable_height / levels

        loc = dict()

        # qm = QFontMetrics(QFont("Times", 10))
        # rect = qm.boundingRect("{}".format(tree[-1][0]))

        for level, nodes in enumerate(tree):
            y = margin + level_height * level
            for idx, node in enumerate(nodes):
                # draw this node
                x = margin + (idx + 1) * usable_width / (len(nodes) + 1)
                rect = QRect(x, y, width, height)
                top = QPoint(x + width / 2, y)
                down = QPoint(x + width / 2, y + height)
                left = QPoint(x, y + height / 2)
                right = QPoint(x + width, y + height / 2)
                loc[id(node)] = (top, down, left, right)
                qp.drawRect(rect)
                if node.mark:
                    qp.fillRect(rect, Qt.cyan)
                qp.drawText(rect, Qt.AlignCenter, "{}".format(node))

                if id(node.parent) in loc:
                    _, parent_down, _, _ = loc[id(node.parent)]
                    qp.save()
                    qp.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap))
                    qp.drawLine(top, parent_down)
                    qp.restore()

                if id(node.left) in loc and node.left != node:
                    _, _, _, sib_right = loc[id(node.left)]
                    qp.save()
                    qp.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap))
                    qp.drawLine(sib_right, left)
                    qp.restore()

    def set_heap(self, heap):
        self.heap = heap

    def level_traversal(self):
        nodes = [[]]
        q = deque()

        for node in self.heap.min().siblings():
            q.append((node, 0))

        while len(q):
            node, level = q.popleft()
            if level == len(nodes):
                nodes.append([])

            nodes[level].append(node)

            for child in node.children():
                q.append((child, level+1))

        return nodes


class FibListWidget(QListWidget):
    def __init__(self, parent=None):
        super(FibListWidget, self).__init__(parent)
        self.elem2items = {}  # Fibonacci Element to QListWidgetItem lookup table
        self.items2elem = {}  # QListWidgetItem to Fibonacci Element lookup table

    def insert_entry(self, entry):
        item = QListWidgetItem(str(entry))
        self.addItem(item)
        self.elem2items[entry] = item
        self.items2elem[item] = entry

    def remove_item(self, entry):
        item = self.elem2items[entry]
        self.takeItem(self.row(item))
        del self.elem2items[entry]
        del self.items2elem[item]

    def get_current_entry(self):
        if self.currentRow() != -1:
            return self.items2elem[self.currentItem()]
        else:
            return None


class FibonacciDemoGui(QFrame):
    def __init__(self, parent=None):
        super(FibonacciDemoGui, self).__init__(parent)

        self.fibtreeview = FibonacciTreeView(self)
        self.heap = FibonacciHeap.FibonacciHeap()

        # Create the form elements
        label1 = QLabel("Label")
        self.label_edit = QLineEdit()
        label2 = QLabel("Priority")
        self.priority_edit = QLineEdit()
        self.priority_edit.setValidator(QDoubleValidator(self.priority_edit))
        self.insert_button = QPushButton("Insert")
        label3 = QLabel("List of Nodes")
        self.list_widget = FibListWidget()
        self.remove_button = QPushButton("Remove")
        label4 = QLabel("Label")
        self.decrease_label = QLineEdit()
        self.decrease_label.setReadOnly(True)
        decrease_label_palette = QPalette()
        decrease_label_palette.setColor(QPalette.Base, Qt.gray)
        self.decrease_label.setPalette(decrease_label_palette)

        label5 = QLabel("Priority")
        self.decrease_priority_edit = QLineEdit()
        self.decrease_key_button = QPushButton("Decrease Key")
        self.extract_min_button = QPushButton("Extract Min")

        vlayout = QVBoxLayout()
        vlayout.addWidget(label1)
        vlayout.addWidget(self.label_edit)
        vlayout.addWidget(label2)
        vlayout.addWidget(self.priority_edit)
        vlayout.addSpacing(2)
        vlayout.addWidget(self.insert_button)
        vlayout.addSpacing(2)
        vlayout.addWidget(label3)
        vlayout.addWidget(self.list_widget)
        vlayout.addWidget(self.remove_button)
        vlayout.addWidget(self.extract_min_button)
        vlayout.addWidget(label4)
        vlayout.addWidget(self.decrease_label)
        vlayout.addWidget(label5)
        vlayout.addWidget(self.decrease_priority_edit)
        vlayout.addWidget(self.decrease_key_button)

        layout = QHBoxLayout()
        layout.addLayout(vlayout)
        layout.addWidget(self.fibtreeview)
        layout.setStretch(0, 1)
        layout.setStretch(1, 10)

        self.setLayout(layout)
        self.setWindowTitle("Fibonacci Heap Visualizer")

        # setup the connections
        self.connect(self.list_widget, SIGNAL("itemSelectionChanged()"), self.update_decrease_form)
        self.connect(self.insert_button, SIGNAL("clicked()"), self.insert_to_heap)
        self.connect(self.extract_min_button, SIGNAL("clicked()"), self.extract_min)
        self.connect(self.remove_button, SIGNAL("clicked()"), self.remove_list_entry)
        self.connect(self.decrease_key_button, SIGNAL("clicked()"), self.decrease_key)

        self._init_heap()

    def sizeHint(self):
        return QSize(1000, 600)

    def _init_heap(self, num=32):
        random.seed(43)
        for index in xrange(num+1):
            entry = self.heap.insert(index, random.randint(0, 99))
            self.list_widget.insert_entry(entry)
        entry = self.heap.extract_min()
        self.list_widget.remove_item(entry)
        self.fibtreeview.set_heap(self.heap)

    def decrease_key(self):
        entry = self.list_widget.get_current_entry()
        try:
            self.heap.decrease_key(entry, int(self.decrease_priority_edit.text()))
            self.fibtreeview.set_heap(self.heap)
            self.list_widget.remove_item(entry)
            self.list_widget.insert_entry(entry)
            self.update()
        except ValueError as e:
            QMessageBox.warning(self, "Decrease Key Error", str(e))

    def insert_to_heap(self):
        if len(self.priority_edit.text()) and len(self.label_edit.text()):
            obj = self.label_edit.text()
            priority = int(self.priority_edit.text())
            entry = self.heap.insert(obj, priority)
            self.list_widget.insert_entry(entry)
            self.fibtreeview.set_heap(self.heap)
            self.update()

    def extract_min(self):
        entry = self.heap.extract_min()
        self.list_widget.remove_item(entry)
        self.fibtreeview.set_heap(self.heap)
        self.update()

    def update_decrease_form(self):
        node = self.list_widget.get_current_entry()
        if node:
            self.decrease_label.setText(str(node.obj))
            self.decrease_priority_edit.setText(str(node.priority))
        else:
            self.decrease_label.setText("")
            self.decrease_priority_edit.setText("")
            self.update()

    def remove_list_entry(self):
        entry = self.list_widget.get_current_entry()
        if entry:
            self.heap.delete(entry)
            self.fibtreeview.heap = self.heap
            self.list_widget.remove_item(entry)
            self.update()


def main():
    app = QApplication(sys.argv)
    diag = FibonacciDemoGui()
    diag.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
