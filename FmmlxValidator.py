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
        self.perform_all_integrity_checks()

    def is_valid(self) -> bool:
        return bool(self.error_log[0])

    def get_is_valid_message(self):
        return "valid." if self.is_valid() and self.integrity_valid() else "INVALID!"

    def get_error_messages(self) -> str:
        return xsd_error_log_as_simple_strings_pretty(self.error_log[1]) + self.integrity_errors

    def perform_all_integrity_checks(self):
        self.integrity_errors = (self.check_instance_integrity() + self.check_generalization_integrity()
                                 + self.abstract_class_check())

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
                return_str += (f"Class <{class_name}> of Instance <{instance_element.getAttribute("name")}> not found!\n")
            if class_found and not level_complies:
                return_str += (f"Level of instance <{instance_element.getAttribute("name")}> is not exactly one below its class\n")
        return return_str

    def check_generalization_integrity(self) -> str:
        not_on_level_zero: bool
        same_level_generalization: bool
        return_str: str = ""
        for gen_elem in self.xml_doc.getElementsByTagName("PureGeneralization"):
            child_class = gen_elem.getAttribute("child")
            parent_class = gen_elem.getAttribute("parent")
            child_class_elem: Element
            parent_class_elem: Element
            for meta_class_elem in self.xml_doc.getElementsByTagName("MetaClass"):
                if meta_class_elem.getAttribute("name") == child_class:
                    child_class_elem = meta_class_elem
                if meta_class_elem.getAttribute("name") == parent_class:
                    parent_class_elem = meta_class_elem
            for instance_elem in self.xml_doc.getElementsByTagName("Instance"):
                if instance_elem.getAttribute("name") == child_class:
                    child_class_elem = instance_elem
                if instance_elem.getAttribute("name") == parent_class:
                    parent_class_elem = instance_elem

            if child_class_elem is None or parent_class_elem is None:
                return_str += f"Child class <{child_class}> or parent class <{parent_class}> not found!"
            else:
                level_of_child: int = int(child_class_elem.getAttribute("level"))
                level_of_parent: int = int(parent_class_elem.getAttribute("level"))
                #C3: same level
                #C4: not level 0
                if level_of_child != level_of_parent:
                    return_str += (f"The level of the child class <{child_class}> is unequal to the level of its parent class"
                                   f"<{parent_class}>! Pure generalizations across levels is prohibited!\n")
                if level_of_child < 1 or level_of_parent < 1:
                    return_str += (f"The level of the child class <{child_class}> or the parent class <{parent_class}> is 0. "
                          f"Pure generalizations may only be added to classes on level greater than  0\n")
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
                    return_str += (f"The instance <{instance_elem.getAttribute("name")}> is an instance of the abstract class"
                                   f"<{abstract_elem.getAttribute("name")}>. Abstract classes must not have any instances!\n")
        return return_str




#test = EasyFmmlxValidator(False, "FMMLx_Example_Diagrams/simple2.xml")
#test.perform_all_integrity_checks()