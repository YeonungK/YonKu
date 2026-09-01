command_name = 'test_hi'
command_text = 'hello'
data_list = {}
command_type = 'READ'
communication_syntax = 'ASCII'
desired_data_type = 'string'

function_code = 'response = "hello, hi, yes, no"\nreturn response'
data_manipulation_code = 'response = response.split(",")\n'

def run(self):
    try:
        response = "hello, hi, yes, no"
        response = response.split(",")
        
        _returned_data = response
        if not isinstance(_returned_data, list):
            raise ValueError('Returned data must be a list.')
        if len(_returned_data) != 4:
            raise ValueError('Returned data length does not match its data type channels.')
        _returned_formats = ['text', 'text', 'text', 'text']
        for _returned_value, _returned_format in zip(_returned_data, _returned_formats):
            if _returned_format == 'integer' and (not isinstance(_returned_value, int) or isinstance(_returned_value, bool)):
                raise ValueError('Returned channel value must be an integer.')
            if _returned_format == 'float' and not isinstance(_returned_value, (int, float)):
                raise ValueError('Returned channel value must be numeric.')
            if _returned_format == 'text' and not isinstance(_returned_value, str):
                raise ValueError('Returned channel value must be text.')
            if _returned_format == 'boolean' and not isinstance(_returned_value, bool):
                raise ValueError('Returned channel value must be boolean.')
        return _returned_data

    except Exception as e:
        print("Something went wrong: " + str(e))
