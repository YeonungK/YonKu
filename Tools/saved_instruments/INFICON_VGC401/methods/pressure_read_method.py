
command_name = "pressure_read"
command_text = "PR1"
data_list = {}
command_type = "READ"
communication_syntax = "ASCII"
desired_data_type = "string"

function_code = """pressure = self.query("PR1")
return pressure"""
data_manipulation_code = """"""
def pressure_read(self):
    try:
        pressure = self.query("PR1")
        pressure = pressure.split(",")
        pressure = pressure[1]
        
        return pressure

    except Exception as e:
        print("Something went wrong: " + e)
