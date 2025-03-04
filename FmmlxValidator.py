from easyxsd_new import *
#xsd = xsd_from_file("FMMLx_Schemas/standardFMMLx.xsd")
#xml_f = xml_from_file("FMMLx_Example_Diagrams/Model_LLM-2.xml")
#xml_t = xml_from_file("FMMLx_Example_Diagrams/standardFMMLx-example1.xml")


#print(xsd_error_log_as_simple_strings_pretty(validate_with_errors(xml_f, xsd)[1]))

#print_xsd_error_log(validate_with_errors(xml_f, xsd)[1])

class easyFmmlxValidator:
    def __init__(self, standard_validation: bool, xml_path: str):
        self.standard_validation = standard_validation
        if self.standard_validation:
            self.fmmlx_schema = xsd_from_file("FMMLx_Schemas/standardFMMLx.xsd")
        else:
            self.fmmlx_schema = xsd_from_file("FMMLx_Schemas/simpleFMMLx.xsd")
        self.fmmlx_doc = xml_from_file(xml_path)
        self.error_log = validate_with_errors(self.fmmlx_doc, self.fmmlx_schema)

    def is_valid(self) -> bool:
        return bool(self.error_log[0])

    def get_is_valid_message(self):
        return "valid." if self.is_valid() else "INVALID!"

    def get_error_messages(self) -> str:
        return xsd_error_log_as_simple_strings_pretty(self.error_log[1])
