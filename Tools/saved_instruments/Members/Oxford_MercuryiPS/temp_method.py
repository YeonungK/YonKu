
command_name = "temp"
command_text = "READ:DEV:MB1.T1:TEMP:SIG:TEMP?"
data_list = {}
command_type = "READ"
communication_syntax = "ASCII"
desired_data_type = "string"

function_code = """sef = self.query("READ:DEV:MB1.T1:TEMP:SIG:TEMP?")
return sef"""
data_manipulation_code = """"""



def temp(self):
    try:
        sef = self.query("READ:DEV:MB1.T1:TEMP:SIG:TEMP?")
        
        return sef

    except Exception as e:
        print("Something went wrong: " + e)
