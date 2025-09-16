from flask import Flask, render_template, request, jsonify
from num2words import num2words
from text2digits import text2digits
import base64
import re

app = Flask(__name__)

def text_to_number(text):
    """convert text number to integer"""
    # use python library to handle conversion of text numbers (including numbers over 10 and hyphens) to digits
    t2d = text2digits.Text2Digits() # Handles numbers above ten, hyphens, 'and', etc.
    result = t2d.convert(text)
    # extract the first sequence of digits from the converted string
    match = re.search(r'\d+', result)
    if match:
        return int(match.group())
    raise ValueError("Unable to convert text to number")

def number_to_text(number):
    """convert integer to English text, with spaces not hyphens"""
    try:
        # num2words returns hyphenated text for some numbers, replace with spaces
        return num2words(number).replace("-", " ")
    except:
        raise ValueError("Unable to convert number to text")

def base64_to_number(b64_str):
    """convert base64 to integer"""
    try:
        # decode base64 string to bytes
        decoded_bytes = base64.b64decode(b64_str)
        # convert bytes to integer (little-endian)
        return int.from_bytes(decoded_bytes, byteorder='little')
    except:
        raise ValueError("Invalid base64 input")

def number_to_base64(number):
    """convert integer to base64"""
    try:
        n = int(number)
        if n == 0:
            b = b'\x00'  # special case for zero
        else:
            # calculate minimum number of bytes needed to represent the integer
            length = (n.bit_length() + 7) // 8 or 1
            b = n.to_bytes(length, byteorder='little')
        # encode bytes to base64 string
        return base64.b64encode(b).decode('utf-8')
    except Exception as e:
        raise ValueError("Unable to convert to base64: " + str(e))

def hex_to_number(h):
    """strictly convert hexadecimal input (no 0x, only digits) to int"""
    # remove leading/trailing whitespace
    h = h.strip()
    # validate that input contains only hexadecimal digits
    if not re.fullmatch(r'[0-9a-fA-F]+', h):
        raise ValueError("Invalid hexadecimal input: must be only 0-9, a-f")
    # convert hexadecimal string to integer
    return int(h, 16)

def octal_to_number(o):
    """convert octal input (no 0o, only digits) to int"""
    o = o.strip()
    if not re.fullmatch(r'[0-7]+', o):
        raise ValueError("Invalid octal input: must be only 0-7")
    return int(o, 8)

def number_to_octal(number):
    """convert integer to octal (without '0o' prefix)"""
    return oct(number)[2:]

@app.route('/')
def index():
    # render the main HTML page
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        input_value = data['input']
        input_type = data['inputType']
        output_type = data['outputType']
        
        # convert input to integer based on input type
        if input_type == 'text':
            number = text_to_number(input_value)
        elif input_type == 'binary':
            number = int(input_value, 2)  # parse binary string to integer
        elif input_type == 'decimal':
            number = int(input_value) # parse decimal string to integer
        elif input_type == 'octal':
            number = octal_to_number(input_value)
        elif input_type == 'hexadecimal':
            number = hex_to_number(input_value)   # use strict hexadecimal helper
        elif input_type == 'base64':
            number = base64_to_number(input_value)
        else:
            raise ValueError("Invalid input type")
            
        # convert integer to output type
        if output_type == 'text':
            result = number_to_text(number)
        elif output_type == 'binary':
            result = bin(number)[2:]              # remove '0b' prefix
        elif output_type == 'octal':
            result = number_to_octal(number)
        elif output_type == 'decimal':
            result = str(number)
        elif output_type == 'hexadecimal':
            result = hex(number)[2:]              # remove '0x' prefix
        elif output_type == 'base64':
            result = number_to_base64(number)
        else:
            raise ValueError("Invalid output type")
            
        # if valid, return result and no error
        return jsonify({'result': result, 'error': None})
    except Exception as e:
        # return error message if any exception occurs
        return jsonify({'result': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)