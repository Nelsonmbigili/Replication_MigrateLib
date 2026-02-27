from __future__ import annotations

import zipfile
import shutil
import os
import re

from mako.template import Template

from typing import List
from typing import Optional

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import xml.dom.minidom as minidom   # minidom used for prettyprint

import vsdx
from .pages import Page
from .pages import PagePosition

from vsdx import Shape

from vsdx import namespace
from vsdx import ext_prop_namespace
from vsdx import vt_namespace
from vsdx import r_namespace
from vsdx import document_rels_namespace
from vsdx import cont_types_namespace

ET.register_namespace('', namespace[1:-1])
ET.register_namespace('', ext_prop_namespace[1:-1])
ET.register_namespace('vt', vt_namespace[1:-1])
ET.register_namespace('r', r_namespace[1:-1])
ET.register_namespace('', document_rels_namespace[1:-1])
ET.register_namespace('', cont_types_namespace[1:-1])


# Other methods and classes remain unchanged...

class VisioFile:
    # Other methods remain unchanged...

    @staticmethod
    def unescape_mako_statements(mako_source):
        # Unescape any text between <% ... %> or ${ ... }
        mako_source_out = mako_source
        matches = re.findall(r'<%(.*?)%>', mako_source)  # non-greedy search for all <%...%> strings
        for m in matches:
            unescaped = m.replace('&gt;', '>').replace('&lt;', '<')
            mako_source_out = mako_source_out.replace(m, unescaped)
        return mako_source_out

    def mako_render_vsdx(self, context: dict):
        """Transform a template VisioFile object using the Mako language
        The method updates the VisioFile object loaded from the template file, so does not return any value.

        :param context: A dictionary containing values that can be accessed by the Mako processor
        :type context: dict

        :return: None
        """
        # Parse each shape in each page as Mako template with context
        pages_to_remove = []  # list of pages to be removed after loop
        for page in self.pages:  # type: Page
            # Check if page should be removed
            if VisioFile.mako_page_showif(page, context):
                loop_shape_ids = list()
                for shapes_by_id in page._shapes:  # type: Shape
                    VisioFile.mako_render_shape(shape=shapes_by_id, context=context, loop_shape_ids=loop_shape_ids)

                source = ET.tostring(page.xml.getroot(), encoding='unicode')
                source = VisioFile.unescape_mako_statements(source)  # Unescape chars like < and > inside <%...%>
                template = Template(source)
                output = template.render(**context)  # Pass context as keyword arguments
                page.xml = ET.ElementTree(ET.fromstring(output))  # Create ElementTree from Element created from output

                # Update loop shape IDs which have been duplicated by Mako template
                page.set_max_ids()
                for shape_id in loop_shape_ids:
                    shapes_by_id = page._find_shapes_by_id(shape_id)  # type: List[Shape]
                    if shapes_by_id and len(shapes_by_id) > 1:
                        delta = 0
                        for shape in shapes_by_id[1:]:  # From the 2nd onwards - leaving original unchanged
                            # Increment each new shape duplicated by the Mako loop
                            self.increment_sub_shape_ids(shape, page)
                            delta += shape.height  # Automatically move each duplicate down
                            shape.move(0, -delta)  # Move duplicated shapes so they are visible
            else:
                # Note page to remove after this loop has completed
                pages_to_remove.append(page)
        # Remove pages after processing
        for p in pages_to_remove:
            print(f"Removing page:'{p.name}' index:{p.index_num}")
            self.remove_page_by_index(p.index_num)

    @staticmethod
    def mako_render_shape(shape: Shape, context: dict, loop_shape_ids: list):
        prev_shape = None
        for s in shape.child_shapes:  # type: Shape
            # Manage for loops in template
            loop_shape_id = VisioFile.mako_create_for_loop_if(s, prev_shape)
            if loop_shape_id:
                loop_shape_ids.append(loop_shape_id)
            prev_shape = s
            # Manage 'set self' statements
            VisioFile.mako_set_selfs(s, context)
            VisioFile.mako_render_shape(shape=s, context=context, loop_shape_ids=loop_shape_ids)

    @staticmethod
    def mako_set_selfs(shape: Shape, context: dict):
        # Apply any <% self self.xxx = yyy %> statements in shape properties
        mako_source = shape.text
        matches = re.findall(r'<% self.(.*?)\s?=\s?(.*?) %>', mako_source)  # Non-greedy search for all <%...%> strings
        for m in matches:  # type: tuple  # Expect ('property', 'value') such as ('x', '10') or ('y', 'n*2')
            property_name = m[0]
            value = "${" + m[1] + "}"  # Mako to be processed
            # TODO: Replace any self references in value with actual value - i.e. <% self.x = self.x+1 %>
            self_refs = re.findall(r'self.(.*)[\s+-/*//]?', m[1])  # Greedy search for all self.? between +, -, *, or /
            for self_ref in self_refs:  # type: tuple  # Expect ('property', 'value') such as ('x', '10') or ('y', 'n*2')
                ref_val = str(shape.__getattribute__(self_ref[0]))
                value = value.replace('self.' + self_ref[0], ref_val)
            # Use Mako template to calculate any self refs found
            template = Template(value)  # Value might be '${1.0+2.4*3}'
            value = template.render(**context)
            if property_name in ['x', 'y']:
                shape.__setattr__(property_name, value)

        # Remove any <% self %> statements, leaving any remaining text
        matches = re.findall('<% self.*?%>', mako_source)
        for m in matches:
            mako_source = mako_source.replace(m, '')  # Remove Mako 'self' statement
        shape.text = mako_source

    @staticmethod
    def mako_page_showif(page: Page, context: dict):
        text = page.name
        mako_source = re.findall(r"<% showif\s(.*?)\s%>", text)
        if len(mako_source):
            # Process last matching value
            template_source = "${" + mako_source[-1] + "}"
            template = Template(template_source)  # Value might be '${1.0+2.4*3}'
            value = template.render(**context)
            # Is the value truthy - i.e. not 0, False, or empty string, tuple, list or dict
            print(f"mako_page_showif(context={context}) statement: {template_source} returns: {type(value)} {value}")
            if value in ['False', '0', '', '()', '[]', '{}']:
                print("value in ['False', '0', '', '()', '[]', '{}']")
                return False  # Page should be hidden
            # Remove Mako statement from page name
            mako_statement = re.match("<%.*?%>", page.name)[0]
            page.name = page.name.replace(mako_statement, '')
        return True  # Page should be left in
