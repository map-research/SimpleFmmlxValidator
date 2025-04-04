from xml.dom.minidom import Document
class SimpleFmmlxModelCreator:
    def __init__(self, model_name: str):
        self.model_name: str = model_name
        self.simple_fmmlx_doc: Document = Document()
        self.root = self.simple_fmmlx_doc.createElement("MultiLevelModel")
        self.root.setAttribute("modelName", self.model_name)
        self.simple_fmmlx_doc.appendChild(self.root)
        self.object_names = []

    def add_class(self, class_name: str):
        class_elem = self.simple_fmmlx_doc.createElement("MetaClass")
        class_elem.setAttribute("name", class_name)
        class_elem.setAttribute("level", "1")
        class_elem.setAttribute("isAbstract", "false")
        self.root.appendChild(class_elem)

    def add_attribute(self, class_name: str, attribute_name: str, attribute_type: str):
        attribute_elem = self.simple_fmmlx_doc.createElement("Attribute")
        attribute_elem.setAttribute("class", class_name)
        attribute_elem.setAttribute("instantiationLevel", "0")
        attribute_elem.setAttribute("name", attribute_name)
        attribute_elem.setAttribute("type", attribute_type)
        self.root.appendChild(attribute_elem)

    def add_object(self, object_name: str, class_name: str):
        object_elem = self.simple_fmmlx_doc.createElement("Instance")
        object_elem.setAttribute("name", object_name)
        object_elem.setAttribute("ofClass", class_name)
        object_elem.setAttribute("isAbstract", "false")
        object_elem.setAttribute("level", "0")
        self.root.appendChild(object_elem)

    def get_object_name(self, class_name: str) -> str:
        i: int = 1
        object_name = class_name + "_" + str(i)
        while object_name in self.object_names:
            i += 1
            object_name = class_name + "_" + str(i)
        self.object_names.append(object_name)
        return object_name

    def add_slot(self, object_name: str, attribute_name: str, slot_value: str):
        slot_elem = self.simple_fmmlx_doc.createElement("SlotValue")
        slot_elem.setAttribute("class", object_name)
        slot_elem.setAttribute("attributeName", attribute_name)
        slot_elem.setAttribute("value", slot_value)
        self.root.appendChild(slot_elem)

    def save(self, save_path: str):
        with open(save_path, 'w') as file:
            file.write(self.simple_fmmlx_doc.toprettyxml(indent='    '))

    def __repr__(self):
        return f"{self.model_name}"
