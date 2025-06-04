from xml.dom import minidom
from xml.dom.minidom import Document, Element

from easyxsd_new import *
#xsd = xsd_from_file("FMMLx_Schemas/standardFMMLx.xsd")
#xml_f = xml_from_file("FMMLx_Example_Diagrams/Model_LLM-2.xml")
#xml_t = xml_from_file("FMMLx_Example_Diagrams/standardFMMLx-example1.xml")


#print(xsd_error_log_as_simple_strings_pretty(validate_with_errors(xml_f, xsd)[1]))

#print_xsd_error_log(validate_with_errors(xml_f, xsd)[1])

class EasyFmmlxValidator:
    def __init__(self, standard_validation: bool, xml_path: str):
        self.standard_validation = standard_validation
        if self.standard_validation:
            self.fmmlx_schema = xsd_from_file("FMMLx_Schemas/standardFMMLx.xsd")
        else:
            self.fmmlx_schema = xsd_from_file("FMMLx_Schemas/simpleFMMLx.xsd")
        self.fmmlx_doc = xml_from_file(xml_path)
        self.xml_doc: Document = minidom.parse(xml_path)
        self.error_log = validate_with_errors(self.fmmlx_doc, self.fmmlx_schema)
        self.integrity_errors = ""
#        self.perform_all_integrity_checks()

    def is_valid(self) -> bool:
        return bool(self.error_log[0])

    def get_is_valid_message(self):
        return "valid." if self.is_valid() and self.integrity_valid() else "INVALID!"

    def get_error_messages(self) -> str:
        return xsd_error_log_as_simple_strings_pretty(self.error_log[1]) + self.integrity_errors

    def perform_all_integrity_checks(self):
        self.integrity_errors = (self.check_instance_integrity() + self.check_generalization_integrity()
                                 + self.abstract_class_check() + self.attribute_for_slots_check()
                                 + self.link_integrity_checks())

    def integrity_valid(self) -> bool:
        if self.integrity_errors == "":
            return True
        else:
            return False


    #CONSTRAINT CHECKS
    def check_instance_integrity(self) -> str:
        class_found: bool
        level_complies: bool
        return_str: str = ""
        for instance_element in self.xml_doc.getElementsByTagName("Instance"):
            #C1: Class exists
            #C2: level complies
            class_found = False
            level_complies = False
            class_name: str = instance_element.getAttribute("ofClass")
            instance_level: int = int(instance_element.getAttribute("level"))+1
            for class_elem in self.xml_doc.getElementsByTagName("MetaClass"):
                if not class_found and class_name == class_elem.getAttribute("name"):
                    class_found = True
                    if instance_level == int(class_elem.getAttribute("level")):
                        level_complies = True
            for class_elem in self.xml_doc.getElementsByTagName("Instance"):
                if not class_found and class_name == class_elem.getAttribute("name"):
                    class_found = True
                    if instance_level == int(class_elem.getAttribute("level")):
                        level_complies = True
            if not class_found:
                return_str += (f"Class <{class_name}> of Instance <{instance_element.getAttribute("name")}> not found!\n\n")
            if class_found and not level_complies:
                return_str += (f"Level of instance <{instance_element.getAttribute("name")}> is not exactly one below its class\n\n")
        return return_str

    def check_generalization_integrity(self) -> str:
        return_str: str = ""
        for gen_elem in self.xml_doc.getElementsByTagName("PureGeneralization"):
            child_class = gen_elem.getAttribute("child")
            parent_class = gen_elem.getAttribute("parent")
            child_class_elem: Element = self._retrieve_class_elem_for_string(gen_elem.getAttribute("child"))
            parent_class_elem: Element = self._retrieve_class_elem_for_string(gen_elem.getAttribute("parent"))

            if child_class_elem is None or parent_class_elem is None:
                return_str += f"Child class <{child_class}> or parent class <{parent_class}> not found!"
            else:
                level_of_child: int = int(child_class_elem.getAttribute("level"))
                level_of_parent: int = int(parent_class_elem.getAttribute("level"))
                #C3: same level
                if level_of_child != level_of_parent:
                    return_str += (f"The level of the child class <{child_class}> is unequal to the level of its parent class "
                                   f"<{parent_class}>! Pure generalizations across levels is prohibited!\n\n")
                # C4: not level 0
                if level_of_child < 1 or level_of_parent < 1:
                    return_str += (f"The level of the child class <{child_class}> or the parent class <{parent_class}> is 0. "
                          f"Pure generalizations may only be added to classes on level greater than  0\n\n")

                child_class_meta_class: str = "MetaClass" if child_class_elem.tagName == "MetaClass" else child_class_elem.getAttribute("ofClass")
                parent_class_meta_class: str = "MetaClass" if parent_class_elem.tagName == "MetaClass" else parent_class_elem.getAttribute("ofClass")

                # C6: generalization with same metaclass
                if child_class_meta_class != parent_class_meta_class:
                    return_str += (f"The pure generalization between <{child_class}> and <{parent_class}> is invalid! "
                                   f"Pure generalizations may only be added to instances of the same class! "
                                   f"But the child class <{child_class}> is an instance of <{child_class_meta_class}>, while "
                                   f"the parent class <{parent_class}> is an instance of <{parent_class_meta_class}>! \n\n")
        return return_str

    def abstract_class_check(self) ->str:
        #C5 no instances for abstract classes
        return_str: str  = ""
        abstract_classes: [Element] = []
        for meta_class_elem in (self.xml_doc.getElementsByTagName("MetaClass")):
            if meta_class_elem.getAttribute("isAbstract") == "true":
                abstract_classes.append(meta_class_elem)
        for instance_elem in self.xml_doc.getElementsByTagName("Instance"):
            if instance_elem.getAttribute("isAbstract") == "true":
                abstract_classes.append(instance_elem)

        for abstract_elem in abstract_classes:
            for instance_elem in self.xml_doc.getElementsByTagName("Instance"):
                if instance_elem.getAttribute("ofClass") == abstract_elem.getAttribute("name"):
                    return_str += (f"The instance <{instance_elem.getAttribute("name")}> is an instance of the abstract class "
                                   f"<{abstract_elem.getAttribute("name")}>. Abstract classes must not have any instances!\n\n")
        return return_str

    def attribute_for_slots_check(self) -> str:
        # C7: check whether attribute of slot actually exists
        return_str: str = ""
        for slot_elem in self.xml_doc.getElementsByTagName("SlotValue"):
            attr_invalid: bool = True
            attr_name = slot_elem.getAttribute("attributeName")
            attr_found: bool = False
            attr_candidates: [Element] = []
            for attr_elem in self.xml_doc.getElementsByTagName("Attribute"):
                if attr_elem.getAttribute("name") == attr_name:
                    attr_found = True
                    attr_candidates.append(attr_elem)
            if len(attr_candidates) == 0:
                attr_invalid = False
                return_str += (f"The slot <{attr_name}> in the instance <{slot_elem.getAttribute("class")}> "
                               f"has never been specified as an attribute!\n\n")
            for attr_candidate in attr_candidates:
                if self._is_ancestor_of(attr_candidate.getAttribute("class"), slot_elem.getAttribute("class")):
                    attr_invalid = False
            if attr_invalid:
                return_str += (f"The slot <{attr_name}> in the instance <{slot_elem.getAttribute("class")}> is invalid! "
                               f"No attribute <{attr_name}> is specified in any ancestor of <{slot_elem.getAttribute("class")}>.\n\n")
        return return_str

    def link_integrity_checks(self) -> str:
        # C8: check whether accessName of Links is correct
        # C9: check source/target ancestors
        return_str: str = ""
        for link_elem in self.xml_doc.getElementsByTagName("Link"):
            link_access_name:str = link_elem.getAttribute("accessName")
            link_source_name: str = link_elem.getAttribute("source")
            link_target_name: str = link_elem.getAttribute("target")
            assoc_found: bool = False
            assoc_for_link_elem: Element
            for assoc_elem in self.xml_doc.getElementsByTagName("Association"):
                if assoc_elem.getAttribute("accessTargetFromSourceName") == link_access_name:
                    assoc_found = True
                    assoc_for_link_elem = assoc_elem
            if not assoc_found:
                return_str += (f"The access name <{link_access_name}> of the link between "
                               f"<{link_source_name}> and <{link_target_name}> has not been found!"
                               f" Remember that the accessName of a link must correspond to the "
                               f"accessTargetFromSourceName of an association.\n\n")
            if assoc_found:
                    if not self._is_ancestor_of(assoc_for_link_elem.getAttribute("source"), link_source_name):
                        return_str += (f"The link <{link_access_name}> between <{link_source_name}> "
                                       f"and <{link_target_name}> is invalid! "
                                       f"<{assoc_for_link_elem.getAttribute("source")}> is not an ancestor of "
                                       f"<{link_source_name}>.\n\n")
                    if not self._is_ancestor_of(assoc_for_link_elem.getAttribute("target"), link_target_name):
                        return_str += (f"The link <{link_access_name}> between <{link_source_name}> "
                                       f"and <{link_target_name}> is invalid! "
                                       f"<{assoc_for_link_elem.getAttribute("target")}> is not an ancestor of "
                                       f"<{link_target_name}>.\n\n")

        return return_str

    def _retrieve_class_elem_for_string(self, class_name: str) -> Element:
        for instance_elem in self.xml_doc.getElementsByTagName("Instance"):
            if instance_elem.getAttribute("name") == class_name:
                return instance_elem
        for meta_class_elem in self.xml_doc.getElementsByTagName("MetaClass"):
            if meta_class_elem.getAttribute("name") == class_name:
                return meta_class_elem

    def _retrieve_parent_class_name(self, child_name: str) -> [str]:
        parent_names: [str] = []
        for gen_elem in self.xml_doc.getElementsByTagName("PureGeneralization"):
            if gen_elem.getAttribute("child") == child_name:
                parent_names.append(gen_elem.getAttribute("parent"))
        return parent_names

    def _is_ancestor_of(self, search_ancestor_name: str, descendant_name: str) -> bool:
        # helper for C6: check attribute for single slot
        descendant_elem: Element = self._retrieve_class_elem_for_string(descendant_name)
        # search elem only works if desc_elem is found as instance in beginning
        # step 1: get class of candidate
        search_elem: Element = self._retrieve_class_elem_for_string(descendant_elem.getAttribute("ofClass"))
        while search_elem is not None:
            current_class_name = search_elem.getAttribute("name")
            # step 2: check whether class was searched ancestor
            if current_class_name == search_ancestor_name:
                return True
            # step 3: check pure generalizations (may be empty if no parents found)
            for parent_name in self._retrieve_parent_class_name(current_class_name):
                if parent_name == search_ancestor_name:
                    return True
            # step 4: get meta class or abort
            if search_elem.tagName == "MetaClass":
                return False
            else:
                search_elem = self._retrieve_class_elem_for_string(search_elem.getAttribute("ofClass"))
        return False




#test = EasyFmmlxValidator(False, "FMMLx_Example_Diagrams/simple2.xml")
#test.perform_all_integrity_checks()