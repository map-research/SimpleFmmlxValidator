file_path: str = "\\examples\\oc_records.sql"

example:str = ("REM INSERTING into UTILITYCO_C2M#ASSET.C1_COMM_RTE_TYPE\n"
               "SET DEFINE OFF;\n"
               "Insert into UTILITYCO_C2M#ASSET.C1_COMM_RTE_TYPE (COMM_RTE_TYPE_CD,BUS_OBJ_CD,COMM_RTE_METH_FLG,FMT_ALG_CD,ALW_DND_FLG,CND_VERIF_STATUS_FLG,BO_DATA_AREA,VERSION,ALW_PCT_STATUS_FLG) values ('CELLPHONE','C1-PersonContactType          ','PHONE','C1-VALPHFMT ','C1AD',null, EMPTY_CLOB(),1,'C1YS'\n"
               "Insert into UTILITYCO_C2M#ASSET.C1_COMM_RTE_TYPE (COMM_RTE_TYPE_CD,BUS_OBJ_CD,COMM_RTE_METH_FLG,FMT_ALG_CD,ALW_DND_FLG,CND_VERIF_STATUS_FLG,BO_DATA_AREA,VERSION,ALW_PCT_STATUS_FLG) values ('WORKPHONE','C1-PersonContactType          ','PHONE','C1-VALPHFMT ','C1DD',null, EMPTY_CLOB(),2,'C1NO'\n"
               "Insert into UTILITYCO_C2M#ASSET.C1_COMM_RTE_TYPE (COMM_RTE_TYPE_CD,BUS_OBJ_CD,COMM_RTE_METH_FLG,FMT_ALG_CD,ALW_DND_FLG,CND_VERIF_STATUS_FLG,BO_DATA_AREA,VERSION,ALW_PCT_STATUS_FLG) values ('PRIMARYEMAIL','C1-PersonContactType          ','EMAIL','C1-VALEMFMT ','C1DD',null, EMPTY_CLOB(),3,'C1NO'\n")


def parse_ddl(ex:str):
    ex_lines = ex.split("\n")
    for line in ex_lines:
        _parse_ddl_line(line)

def _parse_ddl_line(line: str):
    print(line)
    table_name: str = ""
    if line.startswith("REM INSERTING"):
        table_name = line.split(".")[1]
        #print(table_name)
    elif line.startswith("Insert into"):
        attribute_names = line.split("(")[1].split(")")[0].split(",")
        #print(attribute_names)
        value_start = line.find("values ")
        values = line[line.find("values ")+len("values ")+1:len(line)].split(",")
        combo = list(zip(attribute_names, values))
        print(combo)
        #_create_object(table_name)

def _create_object(class_name: str, value_set: [str]):
    print(f"New object for class {class_name} with values: ")

parse_ddl(example)
class DdlParser():
    def __init__(self, dll_path: str):
        self.dll_path = dll_path

