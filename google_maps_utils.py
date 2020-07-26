# -*- coding: utf-8 -*-
# import math
import os
from xml.dom import minidom
import codecs
import sys

from lxml import etree

import PYTHON.core.mathLib as mathLib


def test(kmlFile):
    filename, ext = os.path.splitext(kmlFile)
    newfilename = '%s_TESTS%s' %(filename, ext)
    print 'newfilename =', newfilename

    coordsStr = '51,52,53 54,55,56 57,58,59'

    tree = None

    if True:
        tree = etree.parse(kmlFile)
        root = tree.getroot()

        # namespace = '{%s}' %etree.QName(root).namespace or ''

        document = root[0]

        # On capture un LineString, qu'on modifiera avec nos propres coordonnees:
        lineString = None
        lineStringChildren = list()
        for element in tree.iter(tag=etree.Element):
            tag = etree.QName(element)
            if tag.localname == "LineString":
                lineString = element
                for subElement in lineString.iterdescendants(tag=etree.Element):
                    lineStringChildren.append((subElement.tag, subElement.text, subElement.attrib))
                break

        if not etree.iselement(lineString):
            raise Exception('Something went wrong: Could not find a LineString in %s' %kmlFile)

        placeMark = lineString.getparent()
        # placeMarkAttrs = dict(placeMark.attrib)

        if not etree.iselement(placeMark):
            raise Exception('Something went wrong: Could not find a placeMark for %s' %lineString.tag)


        newPlacemark = etree.SubElement(document, placeMark.tag)

        # On rajoute les voisins du lineString qui sont AVANT
        for sibling in list(lineString.itersiblings(preceding=True))[::-1]:
            xx = etree.SubElement(newPlacemark, sibling.tag, **dict(sibling.attrib))

            isNameElement = etree.QName(xx).localname == 'name'
            text = '%s_simplified' %sibling.text if isNameElement else sibling.text
            xx.text = text


        # On reproduit la structure etalbie a partir d'un lineString quelconque,
        # mais on inserera nos propres coordonnees
        newLineString = etree.SubElement(newPlacemark, lineString.tag, **dict(lineString.attrib))
        for tag, text, attrib in lineStringChildren:
            print tag
            zz = etree.SubElement(newLineString, tag, **attrib)
            if etree.QName(zz).localname == 'coordinates':
                text = coordsStr
            zz.text = text

        # On rajoute les voisins du lineString qui sont APRES
        for sibling in lineString.itersiblings():
            xx = etree.SubElement(newPlacemark, sibling.tag, **dict(sibling.attrib))

            isNameElement = etree.QName(xx).localname == 'name'
            text = '%s_simplified' %sibling.text if isNameElement else sibling.text
            xx.text = text





    if tree:
        _writeLxmlDoc(tree, newfilename)



def filterPoints(kmlFile, filterStep=2):

    xmldoc = minidom.parse(kmlFile)
    mainDoc = xmldoc.getElementsByTagName('Document')[0]
    coords_all = list()
    for elem in xmldoc.getElementsByTagName('Placemark'):
        for lineString in elem.getElementsByTagName('LineString'):
            coordsNode = lineString.getElementsByTagName('coordinates')[0].childNodes[0]
            coords_old = coordsNode.data.strip().split('\n')
            if len(coords_old) >= filterStep:
                coords_new = coords_old[0:-1:filterStep]
                coords_new.append(coords_old[-1])
                coords_all.extend(coords_new)
            else:
                coords_all.extend(coords_old)


    node_placemark   = xmldoc.createElement('Placemark')
    node_name        = xmldoc.createElement('name')
    text_name        = minidom.Text()
    text_name.data   = 'Cycling compilation'
    node_lineString  = xmldoc.createElement('LineString')

    node_tesselate   = xmldoc.createElement('tesselate')

    node_coords      = xmldoc.createElement('coordinates')
    text_coords      = minidom.Text()

    mainDoc.appendChild(node_placemark)
    node_placemark.appendChild(node_name)
    node_placemark.appendChild(node_lineString)
    node_lineString.appendChild(node_tesselate)
    node_lineString.appendChild(node_coords)
    node_coords.appendChild(text_coords)
    node_name.appendChild(text_name)

    # coords_final = coords_all[0:-1:filterStep]
    # coords_final.append(coords_all[-1])
    # text_coords.data = '\n'.join(coords_final)
    text_coords.data = '\n'.join(coords_all)


    filename, ext = os.path.splitext(kmlFile)
    newfilename = '%s_SIMPLIFIED%s' %(filename, ext)
    _writeXmlDoc(xmldoc, newfilename)

def prettify(kmlFile, customSuffix=None):

    fileOut = kmlFile

    if customSuffix:
        noExt, ext = os.path.splitext(kmlFile)
        fileOut = '%s%s%s' %(noExt, customSuffix, ext)

    xmldoc = minidom.parse(kmlFile)
    _writeXmlDoc(xmldoc, fileOut)

def _writeXmlDoc(xmlDoc, filepath):

    # NOTE(combi): Les fichiers peuvent contenir des caracteres non-ascii, donc on doit utiliser un codec pour ecrire le contenu correctement
    toWrite = xmlDoc.toprettyxml(encoding='UTF-8').decode('UTF-8')
    with codecs.open(filepath, 'w', 'UTF-8') as file_object:
        file_object.write(toWrite)


def _writeLxmlDoc(lxmlDoc, filepath):
    toWrite = etree.tostring(lxmlDoc, encoding='UTF-8', pretty_print=True, xml_declaration=True).decode('UTF-8')
    with codecs.open(filepath, 'w', 'UTF-8') as file_object:
        # print 'toWrite =', toWrite
        file_object.write(toWrite)



if __name__ == '__main__':

    print(sys.version)
    # print sys.path

    a = [0,0]
    b = [5,0]
    c = [1.8,2.4]
    va = mathLib.Vector(a)
    vb = mathLib.Vector(b)
    vc = mathLib.Vector(c)

    result = va*2.0
    # print (result, type(result))
    result = mathLib.triangleAreaFrom3Points(va,vb,vc)
    # print (result, type(result))

    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/tests.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-08-31.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-01.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-02.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-03.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-04.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-05.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-06.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-07.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-08.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-09.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-10.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-11.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-12.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-13.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-14.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-15.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-16.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-17.kml', customSuffix='_pretty')
    # prettify('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-18.kml', customSuffix='_pretty')


    # filterPoints('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-16_edited.kml')
    # filterPoints('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-17.kml')
    # filterPoints('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-18.kml')

    # test('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-13.kml')
    # test('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-18_SIMPLIFIED.kml')
    # test('/home/combi/Downloads/velodyssee_2019_testsHoudini/history-2019-09-17.kml')
    # test('/home/combi/Downloads/velodyssee_2019_testsHoudini/tests.kml')
