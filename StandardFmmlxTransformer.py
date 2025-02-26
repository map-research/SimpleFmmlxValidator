from xml.dom import minidom
from xml.dom.minidom import Document


class StandardFmmlxTransformer:
    def __init__(self, simple_fmmlx_path: str):
        self.simple_fmmlx_doc: Document = minidom.parse(simple_fmmlx_path)
        self.model_name: str = self._get_model_name()
        self.package_prefix: str = "Root::"
        self.package: str = self.package_prefix + self.model_name
        self.version: str = "4"

    def write_standard_fmmlx(self, save_path: str):
        doc: Document = Document()
        root = doc.createElement("XModelerPackage")
        root.setAttribute("path", self.package)
        root.setAttribute("version", self.version)
        root.setAttribute("xModelerVersion", "")
        doc.appendChild(root)

        root.appendChild(doc.createElement("Imports"))
        model = doc.createElement("Model")
        model.setAttribute("name", self.package)
        root.appendChild(model)

        # Add MetaClasses
        meta_classes = self._get_meta_classes()
        for name, level, is_abstract in meta_classes:
            meta_class = doc.createElement("addMetaClass")
            meta_class.setAttribute("abstract", is_abstract)
            meta_class.setAttribute("isControlClass", "false")
            meta_class.setAttribute("level", level)
            meta_class.setAttribute("maxLevel", level)
            meta_class.setAttribute("name", name)
            meta_class.setAttribute("package", self.package)
            meta_class.setAttribute("singleton", "false")
            model.appendChild(meta_class)

        # Add Instances
        instances = self._get_instances()
        for name, of_class, level, is_abstract in instances:
            instance = doc.createElement("addInstance")
            instance.setAttribute("abstract", is_abstract)
            instance.setAttribute("isControlClass", "false")
            instance.setAttribute("level", level)
            instance.setAttribute("maxLevel", level)
            instance.setAttribute("name", name)
            instance.setAttribute("of", f"{self.package}::{of_class}")
            instance.setAttribute("package", self.package)
            instance.setAttribute("singleton", "false")
            model.appendChild(instance)

        # Add Generalizations (PureGeneralization -> changeParent)
        generalizations = self._get_generalizations()
        for child, parent in generalizations:
            gen = doc.createElement("changeParent")
            gen.setAttribute("class", f"{self.package}::{child}")
            gen.setAttribute("new", f"{self.package}::{parent}")
            gen.setAttribute("old", "")
            gen.setAttribute("package", self.package)
            model.appendChild(gen)

        # Add Enumerations
        enumerations = self._get_enums()
        for name, values in enumerations.items():
            enum = doc.createElement("addEnumeration")
            enum.setAttribute("name", name)
            model.appendChild(enum)
            for value in values:
                enum_value = doc.createElement("addEnumerationValue")
                enum_value.setAttribute("enum_name", name)
                enum_value.setAttribute("enum_value_name", value)
                model.appendChild(enum_value)

        # Add Attributes
        attributes = self._get_attributes()
        for cls, level, name, raw_type in attributes:
            attr = doc.createElement("addAttribute")
            attr.setAttribute("class", f"{self.package}::{cls}")
            attr.setAttribute("level", level)
            attr.setAttribute("multiplicity", "Seq{1,1,true,false}")
            attr.setAttribute("name", name)
            attr.setAttribute("package", self.package)
            attr.setAttribute("type", self._get_complete_type(raw_type))
            model.appendChild(attr)

        # Add Slots
        slots = self._get_slots()
        for cls, attr, val in slots:
            slot = doc.createElement("changeSlotValue")
            slot.setAttribute("class", f"{self.package}::{cls}")
            slot.setAttribute("package", self.package)
            slot.setAttribute("slotName", attr)
            slot.setAttribute("valueToBeParsed", self._get_parse_value(val))
            model.appendChild(slot)

        # Add Associations
        associations = self._get_assocs()
        for src, tgt, name_assoc, name_src, name_tgt, lvl_src, lvl_tgt, min_src, max_src, min_tgt, max_tgt in associations:
            assoc = doc.createElement("addAssociation")
            assoc.setAttribute("accessSourceFromTargetName", name_src)
            assoc.setAttribute("accessTargetFromSourceName", name_tgt)
            assoc.setAttribute("associationType", "Root::Associations::DefaultAssociation")
            assoc.setAttribute("classSource", f"{self.package}::{src}")
            assoc.setAttribute("classTarget", f"{self.package}::{tgt}")
            assoc.setAttribute("fwName", name_assoc)
            assoc.setAttribute("instLevelSource", lvl_src)
            assoc.setAttribute("instLevelTarget", lvl_tgt)
            assoc.setAttribute("multSourceToTarget", self._get_multiplicity_string(min_src, max_src))
            assoc.setAttribute("multTargetToSource", self._get_multiplicity_string(min_tgt, max_tgt))
            assoc.setAttribute("package", self.package)
            assoc.setAttribute("reverseName", "-1")
            assoc.setAttribute("sourceVisibleFromTarget", "true")
            assoc.setAttribute("targetVisibleFromSource", "true")
            model.appendChild(assoc)

        # Add Links
        links = self._get_links()
        for src, tgt, name in links:
            link = doc.createElement("addLink")
            link.setAttribute("classSource", f"{self.package}::{src}")
            link.setAttribute("classTarget", f"{self.package}::{tgt}")
            link.setAttribute("name", name)
            link.setAttribute("package", self.package)
            model.appendChild(link)

        # Save to file
        with open(save_path, 'w') as file:
            file.write(doc.toprettyxml(indent='    '))

    def _get_model_name(self) -> str:
        return self.simple_fmmlx_doc.getElementsByTagName("MultiLevelModel")[0].getAttribute("modelName")

    def _get_meta_classes(self):
        meta_classes = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("MetaClass"):
            name = elem.getAttribute("name")
            level = elem.getAttribute("level")
            is_abstract = elem.getAttribute("isAbstract")
            meta_classes.append((name, level, is_abstract))
        return meta_classes

    def _get_instances(self):
        instances = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("Instance"):
            name = elem.getAttribute("name")
            of_class = elem.getAttribute("ofClass")
            level = elem.getAttribute("level")
            is_abstract = elem.getAttribute("isAbstract")
            instances.append((name, of_class, level, is_abstract))
        return instances

    def _get_generalizations(self):
        generalizations = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("PureGeneralization"):
            child = elem.getAttribute("child")
            parent = elem.getAttribute("parent")
            generalizations.append((child, parent))
        return generalizations

    def _get_attributes(self):
        attributes = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("Attribute"):
            cls = elem.getAttribute("class")
            level = elem.getAttribute("instantiationLevel")
            name = elem.getAttribute("name")
            typ = elem.getAttribute("type")
            attributes.append((cls, level, name, typ))
        return attributes

    def _get_complete_type(self, raw_type: str) -> str:
        aux_types = ["Date", "MonetaryValue", "Currency"]
        basic_types = ["Float", "Integer", "String", "Boolean"]
        type_prefix = "Root::"
        if raw_type in aux_types:
            type_prefix += "Auxiliary::"
        elif raw_type in basic_types:
            type_prefix += "XCore::"
        else:
            type_prefix += self.model_name + "::"
            raw_type = raw_type.split("::")[1]
        return type_prefix + raw_type

    def _get_slots(self):
        slots = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("SlotValue"):
            cls = elem.getAttribute("class")
            attr = elem.getAttribute("attributeName")
            val = elem.getAttribute("value")
            slots.append((cls, attr, val))
        return slots

    def _get_parse_value(self, raw_value: str) -> str:
        if raw_value.startswith("Enumeration"):
            return self.package + "::" + raw_value.split("::")[1] + "::" + raw_value.split("::")[2]
        elif raw_value.startswith("createDate"):
            return "Auxiliary::Date::" + raw_value
        elif self._is_string(raw_value):
            return self._make_string(raw_value)
        else:
            return raw_value

    def _make_string(self, raw_value: str) -> str:
        parse_values = []
        for sign in raw_value:
            parse_values.append(str(ord(sign)))
        new_string = ",".join(parse_values)
        return f"[{new_string}].asString()"

    def _is_string(self, raw_value: str) -> bool:
        if (self._is_number(raw_value) or self._is_boolean(raw_value)
                or raw_value == "null" or raw_value.startswith("Auxiliary")):
            return False
        else:
            return True
    def _is_number(self, raw_value: str) -> bool:
        try:
            float(raw_value)
            return True
        except ValueError:
            return False

    def _is_boolean(self, raw_value: str) -> bool:
        if raw_value.lower()=="true" or raw_value.lower()=="false":
            return True
        else:
            return False

    def _get_assocs(self):
        associations = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("Association"):
            src = elem.getAttribute("source")
            tgt = elem.getAttribute("target")
            name = elem.getAttribute("associationName")
            associations.append((src, tgt, name,
                                 elem.getAttribute("accessSourceFromTargetName"),
                                 elem.getAttribute("accessTargetFromSourceName"),
                                 elem.getAttribute("instantiationLevelSource"),
                                 elem.getAttribute("instantiationLevelTarget"),
                                 elem.getAttribute("minMultiplicitySourceToTarget"),
                                 elem.getAttribute("maxMultiplicitySourceToTarget"),
                                 elem.getAttribute("minMultiplicityTargetToSource"),
                                 elem.getAttribute("maxMultiplicityTargetToSource"),))
        return associations

    def _get_multiplicity_string(self, min, max) -> str:
        is_unbounded: bool = True if max == "-1" else False
        prefix: str = "Seq{"
        affix: str = ",false}"
        main_txt = min + "," + max + ","
        if is_unbounded:
            main_txt += "false"
        else:
            main_txt += "true"
        return prefix + main_txt + affix

    def _get_links(self):
        links = []
        for elem in self.simple_fmmlx_doc.getElementsByTagName("Link"):
            src = elem.getAttribute("source")
            tgt = elem.getAttribute("target")
            name = elem.getAttribute("accessName")
            links.append((src, tgt, name))
        return links

    def _get_enums(self):
        enumerations = {}
        for elem in self.simple_fmmlx_doc.getElementsByTagName("Enumeration"):
            name = elem.getAttribute("name")
            values = [val.firstChild.nodeValue for val in elem.getElementsByTagName("EnumerationValue")]
            enumerations[name] = values
        return enumerations

