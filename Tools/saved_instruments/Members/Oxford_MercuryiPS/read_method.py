
command_name = "read"
command_text = "READ:DEV:MB1.T1:TEMP:SIG:TEMP?"
data_list = {}
command_type = "READ"
communication_syntax = "ASCII"
desired_data_type = "string"

function_code = """response = self.query("READ:DEV:MB1.T1:TEMP:SIG:TEMP?")
return response"""
data_manipulation_code = """response = response.split(":")
response = response[6]
response = response.replace("K","\n")
"""
