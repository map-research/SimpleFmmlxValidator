from SimpleFmmlxModelCreator import SimpleFmmlxModelCreator


class DdlParser():
    def __init__(self, input_path: str, model_name: str):
        self.fmmlxModelCreator = SimpleFmmlxModelCreator(model_name)
        self.table_name: str = ""
        self.start_of_new_table: bool = False
        self.object_counter: int = 0
        with open(input_path, 'r') as input_file:
            self.all_lines = input_file.readlines()

    def transform_into_fmmlx(self, objects_per_class: int = -1, printProgress: bool = False):
        progress:int = 1
        for line in self.all_lines:
            self._parse_single_line(line.strip(), objects_per_class)
            if printProgress:
                print("Currently at line: " + str(progress) +"\n")
                progress += 1

    def _parse_single_line(self, line: str, objects_per_class: int = -1):
        if line.startswith("REM INSERTING"):
            self.table_name = line.split(".")[1]
            self.start_of_new_table = True
            self.object_counter = 0
            # ADD CLASS FOR TABLE
            self.fmmlxModelCreator.add_class(self.table_name)
        elif line.startswith("Insert into"):
            if objects_per_class >= 0 and self.object_counter < objects_per_class:
                self._parse_insertion_line(line)

    def _parse_insertion_line(self, line: str):
        attribute_names = line.lower().split("(")[1].split(")")[0].split(",")
        slot_values = line[line.find("values ") + len("values ") + 1:len(line)-2].split(",")
        attribute_slot_tuple = list(zip(attribute_names, slot_values))
        attribute_type: str = "String"

        if self.start_of_new_table:
            # ADD ALL ATTRIBUTES FOR CLASS ONCE, type set to String for now
            for attribute_name, slot_value in attribute_slot_tuple:
                if slot_value.strip("'").strip(" ").isnumeric():
                    attribute_type = "Integer"
                else:
                    attribute_type = "String"
                self.fmmlxModelCreator.add_attribute(self.table_name, attribute_name, attribute_type)
            self.start_of_new_table = False

        fmmlx_object_name: str = self.fmmlxModelCreator.get_object_name(self.table_name)
        self.fmmlxModelCreator.add_object(fmmlx_object_name, self.table_name)
        for attribute_name, slot_value in attribute_slot_tuple:
            self.fmmlxModelCreator.add_slot(fmmlx_object_name, attribute_name, slot_value.strip("'").strip(" "))
        self.object_counter += 1

    def save_fmmlx_model(self, save_path: str):
        self.fmmlxModelCreator.save(save_path)


oc_parser = DdlParser('examples\\oc_records.sql', "UtilityCo_C2M")
oc_parser.transform_into_fmmlx(printProgress=False, objects_per_class=4)
oc_parser.save_fmmlx_model("examples/simple-oc.xml")