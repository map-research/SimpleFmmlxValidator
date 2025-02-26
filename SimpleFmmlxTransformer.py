from xml.dom import minidom
from xml.dom.minidom import Document


class SimpleFmmlxTransformer:
    def __init__(self, standard_fmmlx_path: str):
        self.standard_fmmlx_doc: Document = minidom.parse(standard_fmmlx_path)
        self.model_name: str = self._get_model_name()
        self.package_prefix: str = "Root::"
        self.version: str = "4"
        self.xModelerVersion: str = ""  # can be empty per default
        self.package: str = self.package_prefix + self.model_name

    def test(self):
        self._get_meta_classes()

    def write_simple_fmmlx(self, save_path: str):
        doc: Document = Document()
        root = doc.createElement("MultiLevelModel")
        root.setAttribute("modelName", self.model_name)
        doc.appendChild(root)

        meta_classes = self._get_meta_classes()
        for name, level, isAbstract in meta_classes:
            meta_class = doc.createElement('MetaClass')
            meta_class.setAttribute('name', name)
            meta_class.setAttribute('level', level)
            meta_class.setAttribute('isAbstract', isAbstract)
            root.appendChild(meta_class)

        # Add Instances
        instances = self._get_instances()
        for name, of, level, abstract in instances:
            instance = doc.createElement('Instance')
            instance.setAttribute('name', name)
            instance.setAttribute('ofClass', of)
            instance.setAttribute('isAbstract', abstract)
            instance.setAttribute('level', level)
            root.appendChild(instance)

        # Add PureGeneralizations
        generalizations = self._get_generalizations()
        for child, parent in generalizations:
            gen = doc.createElement('PureGeneralization')
            gen.setAttribute('child', child)
            gen.setAttribute('parent', parent)
            root.appendChild(gen)

        # Add Enumerations
        enumerations = self._get_enums()
        for name, values in enumerations.items():
            enum = doc.createElement('Enumeration')
            enum.setAttribute('name', name)
            for value in values:
                enum_value = doc.createElement('EnumerationValue')
                enum_value.appendChild(doc.createTextNode(value))
                enum.appendChild(enum_value)
            root.appendChild(enum)

        # Add Attributes
        attributes = self._get_attributes()
        for cls, level, name, typ in attributes:
            attr = doc.createElement('Attribute')
            attr.setAttribute('class', cls)
            attr.setAttribute('instantiationLevel', level)
            attr.setAttribute('name', name)
            attr.setAttribute('type', typ)
            root.appendChild(attr)

        # Add Slots
        slots = self._get_slots()
        for cls, attr, val in slots:
            slot = doc.createElement('SlotValue')
            slot.setAttribute('class', cls)
            slot.setAttribute('attributeName', attr)
            slot.setAttribute('value', val)
            root.appendChild(slot)

        # Add Associations
        assocs = self._get_assocs()
        for source, target, name, access_name_src, access_name_tgt, instLevelSrc, instLevelTgt, minMultSrc, maxMultSrc, minMultTgt, maxMultTgt in assocs:
            assoc = doc.createElement('Association')
            assoc.setAttribute('source', source)
            assoc.setAttribute('target', target)
            assoc.setAttribute('associationName', name)
            assoc.setAttribute("accessSourceFromTargetName", access_name_src)
            assoc.setAttribute("accessTargetFromSourceName", access_name_tgt)
            assoc.setAttribute('instantiationLevelSource', instLevelSrc)
            assoc.setAttribute('instantiationLevelTarget', instLevelTgt)
            assoc.setAttribute('minMultiplicitySourceToTarget', minMultSrc)
            assoc.setAttribute('maxMultiplicitySourceToTarget', maxMultSrc)
            assoc.setAttribute('minMultiplicityTargetToSource', minMultTgt)
            assoc.setAttribute('maxMultiplicityTargetToSource', maxMultTgt)
            root.appendChild(assoc)

        # Add Links
        links = self._get_links()
        for source, target, name in links:
            link = doc.createElement('Link')
            link.setAttribute('source', source)
            link.setAttribute('target', target)
            link.setAttribute('accessName', name)
            root.appendChild(link)


        # Save to file
        with open(save_path, 'w') as file:
            file.write(doc.toprettyxml(indent='    '))

    def _get_model_name(self) -> str:
        return self.standard_fmmlx_doc.getElementsByTagName("XModelerPackage")[0].getAttribute("path").split("::")[1]

    def _get_meta_classes(self) -> []:
        all_meta_classes = []
        for meta_class_elem in self.standard_fmmlx_doc.getElementsByTagName("addMetaClass"):
            meta_class = (meta_class_elem.getAttribute("name"), meta_class_elem.getAttribute("level"),
                          meta_class_elem.getAttribute("abstract"))
            all_meta_classes.append(meta_class)
        return all_meta_classes

    def _get_instances(self) -> []:
        all_instances = []
        for instance_elem in self.standard_fmmlx_doc.getElementsByTagName("addInstance"):
            instance = (instance_elem.getAttribute("name"), instance_elem.getAttribute("of").split("::")[2],
                        instance_elem.getAttribute("level"), instance_elem.getAttribute("abstract"))
            all_instances.append(instance)
        return all_instances

    def _get_generalizations(self):
        all_generalizations = []
        for generalization_elem in self.standard_fmmlx_doc.getElementsByTagName("changeParent"):
            generalization = (generalization_elem.getAttribute("class").split("::")[2],
                              generalization_elem.getAttribute("new").split("::")[2])
            all_generalizations.append(generalization)
        return all_generalizations

    def _get_attributes(self):
        all_attributes = []
        for attribute_elem in self.standard_fmmlx_doc.getElementsByTagName("addAttribute"):
            attribute = (attribute_elem.getAttribute("class").split("::")[2], attribute_elem.getAttribute("level"),
                         attribute_elem.getAttribute("name"),
                         self._get_attribute_type(attribute_elem.getAttribute("type")))
            all_attributes.append(attribute)
        return all_attributes

    def _get_attribute_type(self, og_type: str) -> str:
        core = og_type.split("::")[1]
        value = og_type.split("::")[2]
        if core == self.model_name:
            return "Enumeration::" + value
        else:
            return value

    def _get_enums(self) -> {}:
        all_enums = {}
        for enum_elem in self.standard_fmmlx_doc.getElementsByTagName("addEnumeration"):
            enum_values = []
            enum_name = enum_elem.getAttribute("name")
            for enum_value_elem in self.standard_fmmlx_doc.getElementsByTagName("addEnumerationValue"):
                if enum_name == enum_value_elem.getAttribute("enum_name"):
                    enum_values.append(enum_value_elem.getAttribute("enum_value_name"))
            all_enums.update({enum_name: enum_values})
        return all_enums

    def _get_links(self):
        all_links = []
        for link_elem in self.standard_fmmlx_doc.getElementsByTagName("addLink"):
            link = (link_elem.getAttribute("classSource").split("::")[2],
                    link_elem.getAttribute("classTarget").split("::")[2],
                    link_elem.getAttribute("name"))
            all_links.append(link)
        return all_links

    def _get_assocs(self):
        all_assocs = []
        for assoc_elem in self.standard_fmmlx_doc.getElementsByTagName("addAssociation"):
            assoc = (assoc_elem.getAttribute("classSource").split("::")[2],
                     assoc_elem.getAttribute("classTarget").split("::")[2],
                     assoc_elem.getAttribute("fwName"),
                     assoc_elem.getAttribute("accessSourceFromTargetName"),
                     assoc_elem.getAttribute("accessTargetFromSourceName"),
                     assoc_elem.getAttribute("instLevelSource"),
                     assoc_elem.getAttribute("instLevelTarget"),
                     assoc_elem.getAttribute("multSourceToTarget")[4:].split(",")[0],
                     assoc_elem.getAttribute("multSourceToTarget")[4:].split(",")[1],
                     assoc_elem.getAttribute("multTargetToSource")[4:].split(",")[0],
                     assoc_elem.getAttribute("multTargetToSource")[4:].split(",")[1],
                     )
            all_assocs.append(assoc)
        return all_assocs

    def _get_slots(self):
        all_slots = []
        for slot_elem in self.standard_fmmlx_doc.getElementsByTagName("changeSlotValue"):
            slot = (slot_elem.getAttribute("class").split("::")[2],
                    slot_elem.getAttribute("slotName"),
                    self._parse_slot_value(slot_elem.getAttribute("valueToBeParsed"))
                    )
            all_slots.append(slot)
        return all_slots

    def _parse_slot_value(self, value: str):
        #three special cases: string, date, enum value
        # CASE 1: STRING
        if value.endswith("asString()"):
            sign_list = value[1:].split("]")[0].split(",")
            value = ""
            if sign_list[0] != "":
                for sign_code in sign_list:
                    value += chr(int(sign_code))
            return value

        # CASE 2: DATE
        if len(value.split("::")) > 1 and value.split("::")[1] == "Date":
            value = value.split("::")[2]
            return value

        # CASE 3 : ENUM
        if len(value.split("::")) > 1 and value.split("::")[1] == self.model_name:
            value = value.split("::")[2] + "::" + value.split("::")[3]
            return "Enumeration::" + value

        return value
