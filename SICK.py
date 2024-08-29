import json
import math
import struct

class SICK_SENSOR:
    def get_byte_to_int_value(self, arr, zero_pos, scale, length):
        measurement_value = 0
        for i in range(length):
            measurement_value |= (arr[i] << (8 * (length - i - 1)))
        
        relative_data = measurement_value * (10 ** scale)
        absolute_data = relative_data + zero_pos
        return absolute_data
    
    def get_byte_to_float_value(self, arr, zero_pos, scale, length):
        measurement_value = 0
        for i in range(length):
            measurement_value |= (arr[i] << (8 * (length - i - 1)))
        measurement_value_bytes = struct.pack('I', measurement_value)
        relative_data = struct.unpack('f', measurement_value_bytes)[0] * (10 ** scale)
        
        absolute_data = relative_data + zero_pos
        return absolute_data
    
    def check_bit(self, byte, position):
        return (byte >> position) & 1
    
    def get_od2000_value(self, json_string):
        data_arr = [0] * 6
        re_arr = [0.0] * 3
        doc = json.loads(json_string)
        for i in range(6):
            data_arr[i] = doc["iolink"]["value"][i]
        re_arr[0] = self.get_byte_to_int_value(data_arr, 130, -6, 6)
        re_arr[1] = self.check_bit(data_arr[5], 0)
        re_arr[2] = self.check_bit(data_arr[5], 1)
        return re_arr

    def get_mpb10_value(self, json_string):
        data_arr = [0] * 20
        value = [0.0] * 4
        doc = json.loads(json_string)
        for i in range(20):
            data_arr[i] = doc["iolink"]["value"][i]
        for i in range(4):
            value[i] = self.get_byte_to_float_value(data_arr[i * 4:i * 4 + 4], 0, 0, 4)
        return value

    def get_wtm10l_value(self, json_string):
        data_arr = [0] * 4
        re_arr = [0] * 3
        doc = json.loads(json_string)
        for i in range(4):
            data_arr[i] = doc["iolink"]["value"][i]
        re_arr[0] = self.get_byte_to_int_value(data_arr, 0, 0, 2)
        re_arr[1] = self.check_bit(data_arr[3], 0)
        re_arr[2] = self.check_bit(data_arr[3], 1)
        return re_arr

    def get_css_value(self, json_string):
        data_arr = [0] * 12
        re_arr = [0] * 6
        doc = json.loads(json_string)
        for i in range(12):
            data_arr[i] = doc["iolink"]["value"][i]
        for i in range(4):
            re_arr[i] = self.get_byte_to_int_value(data_arr[i * 2:i * 2 + 2], 0, 0, 2)
        re_arr[4] = self.check_bit(data_arr[11], 0)
        re_arr[5] = self.check_bit(data_arr[11], 1)
        return re_arr

    def get_pbs_value(self, json_string):
        data_arr = [0] * 5
        re_arr = [0.0] * 3
        doc = json.loads(json_string)
        for i in range(5):
            data_arr[i] = doc["iolink"]["value"][i]
        re_arr[0] = self.get_byte_to_float_value(data_arr, 0, 0, 4)
        re_arr[1] = self.check_bit(data_arr[4], 0)
        re_arr[2] = self.check_bit(data_arr[4], 1)
        return re_arr