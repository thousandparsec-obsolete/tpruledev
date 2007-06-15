import sys, os, xml.dom.minidom
from xml.dom.minidom import Node

class Component(object):
    pass

if not 'Component2' in os.listdir('.'):
    os.mkdir('./Component2')
prop_names = {}

for prop_file in os.listdir('./Property'):
    property = xml.dom.minidom.parse('./Property/' + prop_file)
    prop_names[property.getElementsByTagName("property_id")[0].childNodes[0].data] = property.getElementsByTagName("name")[0].childNodes[0].data

for comp_file in os.listdir('./Component'):
    root = xml.dom.minidom.parse('./Component/' + comp_file)
    comp = Component()
    
    comp.name = root.getElementsByTagName("name")[0].childNodes[0].data
    comp.component_id = root.getElementsByTagName("component_id")[0].childNodes[0].data
    comp.category_id = root.getElementsByTagName("category_id")[0].childNodes[0].data
    comp.description = root.getElementsByTagName("description")[0].childNodes[0].data
    comp.tpcl_requirements = root.getElementsByTagName("tpcl_requirements")[0].childNodes[0].data
    #now the properties associated with this component
    comp.properties = {}
    for prop in root.getElementsByTagName("property"):
        comp.properties[prop.getElementsByTagName("property_id")[0].childNodes[0].data] = prop.getElementsByTagName("tpcl_cost")[0].childNodes[0].data
        
    comp_out = open('./Component2/' + comp_file, 'w')
    comp_out.write('<component>\n')
    comp_out.write('    <name>' + comp.name + '</name>\n')
    comp_out.write('    <component_id>' + comp.component_id + '</component_id>\n')
    comp_out.write('    <category_id>' + comp.category_id + '</category_id>\n')
    comp_out.write('    <description>' + comp.description + '</description>\n')
    comp_out.write('    <tpcl_requirements><![CDATA[' + comp.tpcl_requirements + ']]></tpcl_requirements>\n')
    comp_out.write('    <!--propertylist:-->\n')
    for prop_id in comp.properties:
        comp_out.write('    <property>\n')
        comp_out.write('        <name>' + prop_names[prop_id] + '</name>\n')
        comp_out.write('        <tpcl_cost><![CDATA[' + comp.properties[prop_id] + ']]></tpcl_cost>\n')
        comp_out.write('    </property>\n')
    comp_out.write('</component>')
    comp_out.close()