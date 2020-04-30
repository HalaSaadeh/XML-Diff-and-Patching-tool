import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QFileDialog,QDialog,QTextEdit
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as et
import numpy as np
import time
import xml.dom.minidom
import copy


#Interfaces Classes
class Interface(QDialog):
    file1=""
    file2=""
    next=False
    def __init__(self):
        super(Interface, self).__init__()
        loadUi('interface.ui',self)
        self.setWindowTitle('XMl Versioning Tool')
        self.browseF1.clicked.connect(self.browse_File1)
        self.browseF2.clicked.connect(self.browse_File2)
        self.next.clicked.connect(self.nextpage)
        self.resize(886, 555)
        self.tree1=""
        self.tree2=""
    #insert file browsing code
    @pyqtSlot()
    def browse_File1(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            'c:\\Users\halas\PycharmProjects\IDPA', "XML files (*.xml)")
        self.field1.setText(fname[0])
        self.file1=fname[0]
    @pyqtSlot()
    def browse_File2(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            'c:\\Users\halas\PycharmProjects\IDPA', "XML files (*.xml)")
        self.field2.setText(fname[0])
        self.file2=fname[0]
    @pyqtSlot()
    def nextpage(self):
        next=True
        v1 = open(self.file1, "r")
        v2 = open(self.file2, "r")
        f1 = v1.read()
        f2 = v2.read()
        t1=et.fromstring(f1,parser = et.XMLParser(encoding="unicode"))
        self.tree1=self.docpreprocessing(t1)
        t2=et.fromstring(f2,parser = et.XMLParser(encoding="unicode"))
        self.tree2=self.docpreprocessing(t2)
        Step2.tree1=self.tree1
        Step2.tree2=self.tree2
        Step1.tree1=self.tree1
        Step1.tree2=self.tree2
        Step1.vistrees(step1,Step1.tree1, Step1.tree2)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    # Function Definition
    def docpreprocessing(self,t):
        if t is None:
            return None
        newtree=Element(t.tag)
        for k,v in t.attrib.items():
            attrchild=SubElement(newtree, '@ '+k)
            attrcontent=SubElement(attrchild, v)
        for child in t:
            newtree.append(self.docpreprocessing(child))
        if t.text is not None:
            content=t.text
            contentwords=content.split()
            for word in contentwords:
               c=SubElement(newtree,"( "+word)
           # child=SubElement(newtree,t.text)
        return newtree

class Step1(QDialog):
    tree1 = ""
    tree2 = ""
    def __init__(self):
        super(Step1, self).__init__()
        loadUi('step1.ui',self)
        self.setWindowTitle('Document Preprocessing')
        self.next.clicked.connect(self.nextpage)

    @pyqtSlot()
    def nextpage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def vistrees(self,tree1,tree2):
        self.textEdit = QTextEdit()
        self.textEdit.setText(self.printtree(tree1))
        self.wid1.setWidget(self.textEdit)
        self.textEdit = QTextEdit()
        self.textEdit.setText(self.printtree(tree2))
        self.wid2.setWidget(self.textEdit)
    def printtree(self,tree,level=0):
        out="_"*3*level+tree.tag
        for child in tree:
            out=out+"\n"+ (self.printtree(child,level+1))
        return out
class Step2(QDialog):
    tree1=""
    tree2=""
    add1=[]
    add2=[]
    tree1ld=[]
    tree2ld=[]
    containedintable=dict()
    labelsT1=dict()
    njmatrices=[]
    njes=et.ElementTree()
    njes._setroot(Element("editscript"))
    def __init__(self):
        super(Step2,self).__init__()
        loadUi('step2.ui',self)
        self.setWindowTitle("Step 2")
        self.algorithm.activated.connect(self.similarity)
        self.next.clicked.connect(self.nextpage)

    @pyqtSlot()
    def nextpage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
        Step3FW.tree1 = self.tree1
        Step3FW.tree2=self.tree2
        Step3BW.tree1 = copy.deepcopy(self.tree1)
        Step3BW.tree2 = copy.deepcopy(self.tree2)
        Step3BW.tree1ld.append(LDPair("0", -1, None, 0))
        Step3BW.tree2ld.append(LDPair("0", -1, None, 0))
        self.fillld(Step3BW.tree1ld, Step3BW.add1, Step3BW.tree1, None, 0)
        self.fillld(Step3BW.tree2ld, Step3BW.add2, Step3BW.tree2, None, 0)

    @pyqtSlot()
    def similarity(self):
        #If Chawathe is Selected
        if self.algorithm.currentIndex()==0:

            ted,diff,t=self.chawathe(self.tree1,self.tree2)
            self.ted.setText(str(ted))
            sim = 1 / (1 + ted)
            self.sim.setText(str(round(sim,3)))
            self.speed.setText("%s s " % t)
            self.textEdit = QTextEdit()
            tree=et.ElementTree()
            tree._setroot(diff)
            tree.write("editscriptfw.xml")
#            diffs=self.chawatheeditscript(self.tree1,self.tree2)
#            tree = et.ElementTree()
#            tree._setroot(diffs)
#            tree.write("editscriptfw.xml")
            script=open("editscriptfw.xml","r")
            es=script.read()
            p = xml.dom.minidom.parseString(es)
            self.textEdit.setText(p.toprettyxml())
            self.eswidget.setWidget(self.textEdit)
            reverse=et.ElementTree()
            rev=Element("editscript")
            reverse._setroot(rev)
            for child in tree.getroot():
                if child.tag=="insert":
                    rev.append(Element( "delete", {"index": child.attrib["index"], "parent": child.attrib["parent"], "pos": child.attrib["pos"]}))
                if child.tag=="delete":
                    rev.append(Element( "insert", {"index": child.attrib["index"], "parent": child.attrib["parent"], "pos": child.attrib["pos"]}))
                if child.tag=="update":
                    rev.append(Element("update", {"from": child.attrib["to"], "to": child.attrib["from"]}))
            reverse.write("editscriptbw.xml")
        #If N&J is selected
        if self.algorithm.currentIndex()==1:
            start_time = time.time()
            self.containedintable=self.computecontainedinrelations(self.tree1,self.tree2)
            ted=self.nj(self.tree1,self.tree2)
            self.ted.setText(str(ted))
            t=round((time.time() - start_time),3)
            sim = 1 / (1 + ted)
            self.sim.setText(str(round(sim, 3)))
            self.speed.setText("%s s " % t)
        #If Selkow is selected
        if self.algorithm.currentIndex() == 2:
            start_time = time.time()
            ted=self.selkow(self.tree1,self.tree2)
            self.ted.setText(str(ted))
            t = round((time.time() - start_time), 3)
            sim = 1 / (1 + ted)
            self.sim.setText(str(round(sim, 3)))
            self.speed.setText("%s s " % t)

        CompareES.change(comparees)


    def selkow(self,tree1,tree2):
        def costupd(t1, t2):
            if t1.tag == t2.tag:
                return 0
            else:
                return 1

        def costdel(root):
            if len(root) == 0:
                return 1
            else:
                return len(root) + 1

        def costins(root):
            if len(root) == 0:
                return 1
            else:
                return len(root) + 1


        m=len(list(tree1))
        n=len(list(tree2))
        D=np.zeros((m+1,n+1))
        D[0,0]=costupd(tree1,tree2)

        for i in range(1,m+1):
            D[i,0]=D[i-1,0]+costdel(list(tree1)[i-1])
        for j in range(1,n+1):
            D[0,j]=D[0,j-1]+costins(list(tree2)[j-1])
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                upd=D[i-1,j-1]+self.selkow(list(tree1)[i-1],list(tree2)[j-1])
                ins=D[i,j-1]+costins(list(tree2)[j-1])
                delete=D[i-1,j]+costdel(list(tree1)[i-1])
                D[i,j]=min(upd,ins,delete)
        return D[m,n]


    def chawathe(self,t1,t2):
        start_time = time.time()
        tree1ld=[]
        tree2ld=[]
        self.add1=[]
        self.add2=[]
        tree1ld.append(LDPair("0",-1,None,0))
        tree2ld.append(LDPair("0",-1,None,0))
        #self.fillld(tree1ld, t1)
        #print(t1)
        self.fillld(tree1ld, self.add1, t1,None,0)
        self.fillld(tree2ld, self.add2, t2,None,0)
        Step3FW.add1=self.add1
        Step3FW.add2=self.add2
        rows=len(tree1ld)
        cols=len(tree2ld)
        self.tree1ld=tree1ld
        self.tree2ld=tree2ld
        chmatrix=np.zeros((rows,cols))
        #Similarity
        for i in range(1,rows):
            chmatrix[i,0]=(chmatrix[i-1,0]+1)
        for j in range(1,cols):
            chmatrix[0,j]=chmatrix[0,j-1]+1
        for i in range(1, rows):
            for j in range(1,cols):
                insert=sys.maxsize
                update=sys.maxsize
                delete=sys.maxsize
                if tree1ld[i].depth==tree2ld[j].depth:
                    if tree1ld[i].label == tree2ld[j].label:
                        costupdate=0
                    else:
                        costupdate=1
                    update=chmatrix[i-1,j-1]+costupdate
                if tree1ld[i].depth>=tree2ld[j].depth or j==cols-1:
                    delete=chmatrix[i-1,j]+1
                if tree1ld[i].depth<=tree2ld[j].depth or i==rows-1:
                    insert=chmatrix[i,j-1]+1
                chmatrix[i,j]=min(insert,delete,update)
        t = round((time.time() - start_time), 3)
        #Edit Script
        i=rows-1
        j=cols-1
        es=Element("editscript")
        n=1
        a=0
        deleted=[]
        inserted=[]
        while (i>0 and j>0):
            if chmatrix[i,j]==(chmatrix[i-1,j]+1) and ( tree1ld[i].depth >= tree2ld[j].depth or j == cols-1):
                m = j+2
                pos = 0
                while True and m > 0 and i < len(tree1ld):
                    if tree2ld[m].label == tree1ld[i].parent.label and tree2ld[m].depth == tree1ld[i].parent.depth \
                            and tree2ld[m].parent.label == tree1ld[i].parent.parent.label \
                            and tree2ld[m].pos == tree1ld[i].parent.pos:
                        break
                    m = m - 1
                es.insert(0, Element("delete", {"index": str(i - 1), "parent": str(m - 1), "pos": str(tree1ld[i].pos)}))
                i = i - 1
            elif chmatrix[i,j]==chmatrix[i,j-1]+1 and (tree1ld[i].depth <= tree2ld[j].depth or i == rows - 1):
                m = i+2
                pos = 0
                if len(inserted)>0:
                    if inserted[-1].parent is tree2ld[j]:
                        inserts = es.findall("insert")
                        inserts[0].attrib["parent"] = "n" + str(len(inserted)+1)
                while True and m > 0 and j < len(tree2ld):
                    if tree1ld[m].label == tree2ld[j].parent.label and tree1ld[m].depth == tree2ld[j].parent.depth \
                            and tree1ld[m].parent.label == tree2ld[j].parent.parent.label \
                            and tree1ld[m].pos == tree2ld[j].parent.pos:
                        break
                    m = m - 1
                es.insert(0, Element("insert",
                                         {"index": str(j - 1), "parent": str(m - 1), "pos": str(tree2ld[j].pos)}))
                inserted.append(tree2ld[j])
                j = j - 1
            else:
                if not tree1ld[i].label == tree2ld[j].label:
                    es.insert(0, Element("update", {"from": str(i - 1), "to": str(j - 1)}))
                i = i - 1
                j = j - 1

        while i>0:
            m = j+2
            pos = 0
            while True and m > 0 and i < len(tree1ld):
                if tree2ld[m].label == tree1ld[i].parent.label and tree2ld[m].depth == tree1ld[i].parent.depth \
                        and tree2ld[m].parent.label == tree1ld[i].parent.parent.label \
                        and tree2ld[m].pos == tree1ld[i].parent.pos:
                    break
                m = m - 1
            es.insert(0, Element("delete", {"index": str(i - 1), "parent": str(m - 1), "pos": str(tree1ld[i].pos)}))

            i = i - 1
        while j>0:
            m = i+2
            pos = 0

            a = 0
            while a < len(inserted) :
                if inserted[a].parent is tree2ld[j]:
                    inserts=es.findall("insert")
                    inserts[len(inserted)-1].attrib["parent"]="n"+str(a)
            while True and m > 0 and j < len(tree2ld):
                if tree1ld[m].label == tree2ld[j].parent.label and tree1ld[m].depth == tree2ld[j].parent.depth \
                        and tree1ld[m].parent.label == tree2ld[j].parent.parent.label \
                        and tree1ld[m].pos == tree2ld[j].parent.pos\
                        and tree1ld[m].parent.pos == tree2ld[j].parent.parent.pos:
                    break
                    m = m - 1
            es.insert(0, Element("insert",
                                     {"index": str(j - 1), "parent": str(m - 1), "pos": str(tree2ld[j].pos),
                                      "id": "n" + str(len(inserted))}))
            inserted.append(tree2ld[j])
            j = j - 1
        return chmatrix[rows - 1, cols - 1], es,t



    def fillld(self,t,ad,root,parent,pos,level=0):
        rootld=LDPair(root.tag,level,parent,pos)
        rootld.add=root
        t.append(rootld)

        ad.append(root)
        pos=0
        for child in root:
            self.fillld(t,ad,child,rootld,pos,level+1)
            pos=pos+1
        return t

    def computecontainedinrelations(self,t1,t2):
        labelsT1=dict()
        def filldict(t1):
            if t1 is None:
                return
            if t1.tag in labelsT1:
                labelsT1[t1.tag].append(t1)
            else:
                labelsT1[t1.tag]=list()
                labelsT1[t1.tag].append(t1)
            for child in t1:
                filldict(child)
        filldict(t1)

        leafsT2=[]
        #internal function start
        def get_leaf_nodes(root):
            if root is not None:
                if len(list(root))==0:
                    leafsT2.append(root)
                for child in root:
                    get_leaf_nodes(child)
        #internal function end

        get_leaf_nodes(t2)
        for leaf in leafsT2:
            if leaf.tag in self.labelsT1:
                self.containedintable[leaf.tag]=self.labelsT1[leaf.tag]


        self.labelsT1=labelsT1

    def nonleafcontainedins(self,t1,t2):
        print()

    def containedin(self, treeA, treeB):
        all_descendants = list(treeA.iter())
        allB=list(treeB.iter())
        for b in allB:

            if b.tag==treeA.tag:
                allsubB=list(b.iter())
                m=0
                n=0

                found=0
                while n<len(allsubB):
                    if found == len(all_descendants):
                        break
                    if all_descendants[m].tag==allsubB[n].tag:
                        found=found+1
                        n=n+1
                        m=m+1
                    else:
                        n=n+1
                if found==len(all_descendants):
                    return True
                else:
                    return False



    def nj(self,t1,t2):
        tree1=[]
        tree2=[]
        tree1.append(t1)
        tree2.append(t2)
        for child in t1:
            tree1.append(child)
        for child in t2:
            tree2.append(child)
        rows=len(tree1)
        cols=len(tree2)
        njmatrix = np.zeros((rows, cols))
        njmatrix[0,0]=self.njcostupdate(tree1[0],tree2[0])
        self.njmatrices.append(njmatrix)
        for i in range(1,rows):
            njmatrix[i,0]=njmatrix[i-1,0]+self.costdeletetree(t2,tree1[i])
        for j in range(1,cols):
            njmatrix[0,j]=njmatrix[0,j-1]+self.costinserttree(t1,tree2[j])
        for i in range(1,rows):
            for j in range(1, cols):
                ins=njmatrix[i,j-1]+self.costinserttree(t1,tree2[j])
                delt=njmatrix[i-1,j]+self.costdeletetree(t2,tree1[i])
                update=njmatrix[i-1][j-1]+self.nj(tree1[i],tree2[j])
                njmatrix[i,j]=min(ins,delt,update)
        return njmatrix[rows-1,cols-1]



    def njcostupdate(self,tree1,tree2):
        if tree1.tag==tree2.tag:
            cost=0
        else:
            cost=1
        return cost

    def costinserttree(self,source,tree):
        if self.containedin(tree,source):
            cost=1
        else:
            cost=0
            all_descendants = list(tree.iter())
            for a in all_descendants:
                cost=cost+1
        return cost
    def costdeletetree(self,dest,tree):
        if self.containedin(tree,dest):
            cost=1
        else:
            cost = 0
            all_descendants = list(tree.iter())
            for a in all_descendants:
                cost = cost + 1
        return cost


class LDPair():
    label=""
    depth=0
    parent=None
    pos=0
    id=0
    add=None
    def __init__(self,label, depth,parent,pos):
        self.label=label
        self.depth=depth
        self.parent=parent
        self.pos=pos
    def printld(self):
        print(self.label, ",",self.depth)

class CompareES(QDialog):
    def __init__(self):
        super(CompareES, self).__init__()
        loadUi('comparees.ui',self)
        self.setWindowTitle('Compare Edit Scripts')
        self.next.clicked.connect(self.nextpage)

    @pyqtSlot()
    def nextpage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
        Step3FW.patch(step3fw,Step3FW.tree1,Step3FW.tree2)
    def change(self):
        script = open("editscriptfw.xml", "r")
        es = script.read()
        p = xml.dom.minidom.parseString(es)
        self.textEdit = QTextEdit()
        self.textEdit.setText(p.toprettyxml())
        self.es1widget.setWidget(self.textEdit)
        script = open("editscriptbw.xml", "r")
        es = script.read()
        p = xml.dom.minidom.parseString(es)
        self.textEdit = QTextEdit()
        self.textEdit.setText(p.toprettyxml())
        self.es2widget.setWidget(self.textEdit)
class Step3FW(QDialog):
    tree1=""
    tree2=""
    add1=[]
    add2=[]

    def __init__(self):
        super(Step3FW, self).__init__()
        loadUi('step3.ui', self)
        self.setWindowTitle('Patching')
        self.next.clicked.connect(self.nextpage)

    @pyqtSlot()
    def nextpage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
        step3bw.patch(step3bw.tree1,step3bw.tree2)
    def patch(self,t1,t2):
        v=open("editscriptfw.xml","r")
        file = v.read()
        es=et.fromstring(file)
        inserted=[]
        for command in es:
            if command.tag =="delete":
                for a in step2.tree1ld:
                    if a.depth==step2.tree1ld[int(command.attrib["index"])+1].depth-1:
                        for child in a.add:
                            if child is step2.tree1ld[int(command.attrib["index"])+1].add:
                                if not len(list(child))==0:
                                    for c in child:
                                        list(a.add)[list(a.add).index(child)-1].append(c)
                                a.add.remove(child)
            if command.tag == "insert":
                if command.attrib["parent"][0]=="n":
                    m = Element(self.add2[int(command.attrib["index"])].tag)
                    inserted[-1].append(m)
                else:
                    m=Element(self.add2[int(command.attrib["index"])].tag)
                    self.add1[int(command.attrib["parent"])].insert(int(command.attrib["pos"]), m)
                    inserted.append(m)
                    for b in list(self.add1[int(command.attrib["parent"])])[int(command.attrib["pos"])-1]:
                       # print(len(list(list(self.add1[int(command.attrib["parent"])])[int(command.attrib["pos"])-1])))
                        for mk in list(list(self.add1[int(command.attrib["parent"])])[int(command.attrib["pos"])-1]):
                            print(mk)
                            if mk in self.add1:
                            #print(b)
                                list(self.add1[int(command.attrib["parent"])])[int(command.attrib["pos"])-1].remove(mk)
                                m.append(mk)

            if command.tag == "update":
                step2.tree1ld[int(command.attrib["from"])+1].add.tag=step2.tree2ld[int(command.attrib["to"])+1].add.tag

        self.textEdit = QTextEdit()
        self.textEdit.setText(Step1.printtree(step1,self.tree1))
        self.wid2.setWidget(self.textEdit)
        self.textEdit = QTextEdit()
        self.textEdit.setText(Step1.printtree(step1,Step2.tree2))
        self.wid1.setWidget(self.textEdit)
        tree = et.ElementTree()
        tree._setroot(self.tree1)
        tree.write("new.xml")
        ted,s=Step2.chawathe(step2,Step1.tree2, self.tree1)
        self.ted2.setText(str(ted))
        sim=1/(1+ted)
        self.sim.setText(str(sim))
        Step4.newt1=self.tree1

class Step3BW(QDialog):
    tree1 = ""
    tree2 = ""
    add1 = []
    add2 = []
    tree1ld=[]
    tree2ld=[]
    def __init__(self):
        super(Step3BW, self).__init__()
        loadUi('step3pt2.ui', self)
        self.setWindowTitle('Patching')
        self.next.clicked.connect(self.nextpage)

    @pyqtSlot()
    def nextpage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
        Step4.newt2=self.tree2
        Step42.newt1=Step3FW.tree1
        Step42.postprocess(step42)
        Step4.postprocess(step4)

    def patch(self,t1,t2):
        v=open("editscriptbw.xml","r")
        file = v.read()
        es=et.fromstring(file)
        inserted=[]
        for command in es:
            if command.tag =="delete":
                for a in self.tree2ld:
                    if a.depth==self.tree2ld[int(command.attrib["index"])+1].depth-1:
                        for child in a.add:
                            if child is self.tree2ld[int(command.attrib["index"])+1].add:
                                if not len(list(child)) == 0:
                                    for c in child:
                                        list(a.add)[list(a.add).index(child) - 1].append(c)
                                a.add.remove(child)
            if command.tag == "insert":
                if command.attrib["parent"][0] == "n":
                    m = Element(self.add1[int(command.attrib["index"])].tag)
                    inserted[-1].append(m)
                else:
                    m=Element(self.add1[int(command.attrib["index"])])
                    self.add2[int(command.attrib["parent"])].insert(int(command.attrib["pos"]), m.tag)
                    for b in list(self.add2[int(command.attrib["parent"])])[int(command.attrib["pos"])-1]:
                        for mk in list(list(self.add2[int(command.attrib["parent"])])[int(command.attrib["pos"]) - 1]):
                            print(mk)
                            if mk in self.add2:
                                # print(b)
                                list(self.add2[int(command.attrib["parent"])])[int(command.attrib["pos"]) - 1].remove(
                                    mk)
                                m.append(mk)
            if command.tag == "update":
                self.add2[int(command.attrib["from"])].tag=self.add1[int(command.attrib["to"])].tag
        self.textEdit = QTextEdit()
        self.textEdit.setText(Step1.printtree(step1,self.tree2))
        self.wid2.setWidget(self.textEdit)
        self.textEdit = QTextEdit()
        self.textEdit.setText(Step1.printtree(step1,self.tree1))
        self.wid1.setWidget(self.textEdit)
        ted,s=Step2.chawathe(step2,self.tree1, self.tree2)
        self.ted2.setText(str(ted))
        sim = 1 / (1 + ted)
        self.sim.setText(str(sim))
        Step4.newt1=self.tree1

class Step4(QDialog):
    newt1=""
    newt2=""
    def __init__(self):
        super(Step4,self).__init__()
        loadUi('step4.ui',self)
        self.setWindowTitle('Document Postprocessing')
        self.next.clicked.connect(self.nextpage)

    @pyqtSlot()
    def nextpage(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def postprocess(self):
        t1=self.docpostprocessing(self.newt1)
      #  t2=self.docpostrocessing(newt2)
        tree= et.tostring(t1, encoding="unicode")
        myfile = open("newfile1.xml", "w")
        myfile.write(tree)
       # tree = et.ElementTree()
       # tree._setroot(self.t2)
        #tree.write("newfile2.xml")
        script = open("newfile1.xml", "r")
        es = script.read()
        p = xml.dom.minidom.parseString(es)
        self.textEdit = QTextEdit()
        self.textEdit.setText(p.toprettyxml())
        self.wid.setWidget(self.textEdit)

    def docpostprocessing(self, t):
        if t is None:
            return None
        newtree = Element(t.tag)
        for child in t:
            if child.tag[0]=='@':
                for attrchild in child:
                    content=attrchild.tag
                    newtree.attrib[child.tag[2:]]=content
            elif child.tag[0]=='(':
                out=""
                if not newtree.text is None:
                    out=newtree.text+""
                out=out+child.tag[2:]
                newtree.text=out
            else:
                newtree.append(self.docpostprocessing(child))
        return newtree

class Step42(QDialog):
    newt2=None
    def __init__(self):
        super(Step42,self).__init__()
        loadUi('step4pt2.ui',self)
        self.setWindowTitle('Document Postprocessing')

    def postprocess(self):
        t1=self.docpostprocessing(self.newt1)
      #  t2=self.docpostrocessing(newt2)
        tree= et.tostring(t1, encoding="unicode")
        myfile = open("newfile2.xml", "w")
        myfile.write(tree)
       # tree = et.ElementTree()
       # tree._setroot(self.t2)
        #tree.write("newfile2.xml")
        script = open("newfile2.xml", "r")
        es = script.read()
        p = xml.dom.minidom.parseString(es)
        self.textEdit = QTextEdit()
        self.textEdit.setText(p.toprettyxml())
        self.wid.setWidget(self.textEdit)

    def docpostprocessing(self, t):
        if t is None:
            return None
        newtree = Element(t.tag)
        for child in t:
            if child.tag[0]=='@':
                for attrchild in child:
                    content=attrchild.tag
                    newtree.attrib[child.tag[2:]]=content
            elif child.tag[0]=='(':
                out=""
                if not newtree.text is None:
                    out=newtree.text+""
                out=out+child.tag[2:]
                newtree.text=out
            else:
                newtree.append(self.docpostprocessing(child))
        return newtree

#Overwriting system exception
# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook



app = QApplication(sys.argv)
mainwindow=Interface()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedHeight(555)
widget.setFixedWidth(866)
widget.show()
print(mainwindow.tree1)
step1=Step1()
step2=Step2()
comparees=CompareES()
widget.addWidget(step1)
widget.addWidget(step2)
widget.addWidget(comparees)
step3fw=Step3FW()
widget.addWidget(step3fw)
step3bw=Step3BW()
widget.addWidget(step3bw)
step4=Step4()
widget.addWidget(step4)
step42=Step42()
widget.addWidget(step42)
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
