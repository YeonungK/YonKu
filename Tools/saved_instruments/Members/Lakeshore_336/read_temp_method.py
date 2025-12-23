
command_name = "read_temp"
command_text = "KRDG? {Data1}"
data_list = {'Data0': ''}
command_type = "READ"
communication_syntax = "ASCII"
desired_data_type = "string"

function_code = """sef = self.query("KRDG? {Data1}")
return sef"""
data_manipulation_code = """"""
def read_temp(self):
    try:
        sef = self.query("KRDG? ")
        
        return sef

    except Exception as e:
        print("Something went wrong: " + e)
