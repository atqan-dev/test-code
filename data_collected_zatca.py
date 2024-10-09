# if portal_type == "Sandbox":
#     customoid = encode_customoid("TESTZATCA-Code-Signing")
# elif portal_type == "Simulation":
#     customoid = encode_customoid("PREZATCA-Code-Signing")
# else:
#     customoid = encode_customoid("ZATCA-Code-Signing")
#  ===================
from fast_xml_parser import XMLParser
import logging
import copy

class XMLDocument:
    def __init__(self, xml_str=None):
        self.parser_options = {
            'ignoreAttributes': False,
            'ignoreDeclaration': False,
            'ignorePiTags': False,
            'parseTagValue': False
        }
        parser = XMLParser(self.parser_options)
        if xml_str:
            self.xml_object = parser.parse(xml_str) or {}
        else:
            self.xml_object = {'?xml': {'@_version': '1.0', '@_encoding': 'UTF-8'}}

    def get_element(self, xml_object, path_query, parent_xml_object=None, last_tag=None):
        if path_query == "" or not xml_object:
            return xml_object, parent_xml_object, last_tag
        current_path = path_query.split("/")
        current_tag = current_path.pop(0)
        new_query_path = "/".join(current_path)
        return self.get_element(xml_object.get(current_tag), new_query_path, xml_object, current_tag)

    @staticmethod
    def filter_by_condition(result, condition):
        return [item for item in result if all(item.get(k) == v for k, v in condition.items())]

    def get(self, path_query, condition=None):
        if not self.xml_object:
            return None
        xml_object, _, _ = self.get_element(self.xml_object, path_query or "")
        query_result = xml_object
        if query_result and not isinstance(query_result, list):
            query_result = [query_result]
        if condition:
            query_result = self.filter_by_condition(query_result, condition)
        return query_result if query_result else None

    def delete(self, path_query, condition=None):
        if not self.xml_object:
            return False
        xml_object, parent_xml_object, last_tag = self.get_element(self.xml_object, path_query or "")
        query_result = xml_object
        if query_result and not isinstance(query_result, list):
            query_result = [query_result]
        if condition:
            query_result = self.filter_by_condition(query_result, condition)
        if not query_result:
            return False
        if isinstance(parent_xml_object[last_tag], list):
            parent_xml_object[last_tag] = [
                element for element in parent_xml_object[last_tag]
                if not all(element.get(k) == v for k, v in condition.items())
            ]
            if not parent_xml_object[last_tag]:
                del parent_xml_object[last_tag]
        else:
            del parent_xml_object[last_tag]
        return True

    # The set method is not provided in the original code, so it's not included here.

