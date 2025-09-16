import pytest
from index import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# basic route check, to ensure test suite works
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<html' in response.data  # crude HTML check

# check for the explicit cases outlined in the homework

# test 42 to binary
def test_decimal_to_binary_example(client):
    response = client.post('/convert', json={
        'input': '42',
        'inputType': 'decimal',
        'outputType': 'binary'
    })
    data = response.get_json()
    assert data['result'] == '101010'
    assert data['error'] is None

# test forty two to 42
def test_text_to_decimal_example(client):
    response = client.post('/convert', json={
        'input': 'forty two',
        'inputType': 'text',
        'outputType': 'decimal'
    })
    data = response.get_json()
    assert data['result'] == '42'
    assert data['error'] is None

# test 2a to forty two
def test_hex_to_text_example(client):
    response = client.post('/convert', json={
        'input': '2a',
        'inputType': 'hexadecimal',
        'outputType': 'text'
    })
    data = response.get_json()
    assert data['result'] == 'forty two'
    assert data['error'] is None

# coverage tests

# text to other format parameter test
@pytest.mark.parametrize(
    "input_text,outputType,expected",
    [
        ("one hundred and twenty five", "decimal", "125"),  
        ("forty two", "decimal", "42"),                     
        ("sixty nine", "hexadecimal", "45"),                        
        ("ten", "binary", "1010"),                          
        ("eleven", "base64", "Cw=="),                       
        ("twenty one", "octal", "25"),   
    ]
)
def test_convert_text_to_others(client, input_text, outputType, expected):
    # send POST request to /convert with text input and desired output type
    response = client.post('/convert', json={
        'input': input_text,
        'inputType': 'text',
        'outputType': outputType
    })
    data = response.get_json()
    # make sure the conversion result matches expected output and no error occurred
    assert data['result'] == expected
    assert data['error'] is None

# decimal to other format parameter test
@pytest.mark.parametrize(
    "input_val,outputType,expected",
    [
        ("127", "text", "one hundred and twenty seven"),
        ("8", "binary", "1000"),
        ("255", "hexadecimal", "ff"),
        ("14", "base64", "Dg=="),     
        ("42", "binary", "101010"),   
        ("42", "octal", "52"),   
    ]
)
def test_convert_decimal_to_others(client, input_val, outputType, expected):
    response = client.post('/convert', json={
        'input': input_val,
        'inputType': 'decimal',
        'outputType': outputType
    })
    data = response.get_json()
    assert data['result'] == expected
    assert data['error'] is None

# binary to other format parameter test
@pytest.mark.parametrize(
    "input_val,outputType,expected",
    [
        ("101", "text", "five"),
        ("11111111", "decimal", "255"),
        ("11000", "hexadecimal", "18"),
        ("10000000", "base64", "gA=="),
        ("101010", "octal", "52"), 
    ]
)
def test_convert_binary_to_others(client, input_val, outputType, expected):
    response = client.post('/convert', json={
        'input': input_val,
        'inputType': 'binary',
        'outputType': outputType
    })
    data = response.get_json()
    assert data['result'] == expected
    assert data['error'] is None

# hexadecimal to other format parameter test
@pytest.mark.parametrize(
    "input_val,outputType,expected",
    [
        ("b", "text", "eleven"),
        ("f0", "decimal", "240"),
        ("a", "binary", "1010"),
        ("10", "base64", "EA=="),  
        ("2a", "text", "forty two"), # README example
        ("2a", "octal", "52"),      
    ]
)
def test_convert_hex_to_others(client, input_val, outputType, expected):
    response = client.post('/convert', json={
        'input': input_val,
        'inputType': 'hexadecimal',
        'outputType': outputType
    })
    data = response.get_json()
    assert data['result'] == expected
    assert data['error'] is None

# octal to other format parameter test
@pytest.mark.parametrize(
    "input_val,outputType,expected",
    [
        ("52", "decimal", "42"),         
        ("52", "text", "forty two"),    
        ("52", "hexadecimal", "2a"),  
        ("52", "binary", "101010"),   
    ]
)
def test_convert_octal_to_others(client, input_val, outputType, expected):
    response = client.post('/convert', json={
        'input': input_val,
        'inputType': 'octal',
        'outputType': outputType
    })
    data = response.get_json()
    assert data['result'] == expected
    assert data['error'] is None

# base64 to other format parameter test
@pytest.mark.parametrize(
    "input_val,outputType,expected",
    [
        ("Aw==", "decimal", "3"),      
        ("gA==", "binary", "10000000"),
        ("Dg==", "text", "fourteen"),  
        ("EA==", "hexadecimal", "10"),
        ("Mg==", "octal", "62"), 
    ]
)
def test_convert_base64_to_others(client, input_val, outputType, expected):
    response = client.post('/convert', json={
        'input': input_val,
        'inputType': 'base64',
        'outputType': outputType
    })
    data = response.get_json()
    assert data['result'] == expected
    assert data['error'] is None

# paremetrize set of error cases
@pytest.mark.parametrize(
    "payload",
    [
        {'input': 'foo', 'inputType': 'unknown', 'outputType': 'decimal'},
        {'input': '12', 'inputType': 'decimal', 'outputType': 'unknown'},
        {'input': 'nonsense', 'inputType': 'decimal', 'outputType': 'text'},
        {'input': 'notbinary', 'inputType': 'binary', 'outputType': 'decimal'},
        {'input': '0x123', 'inputType': 'hexadecimal', 'outputType': 'decimal'},
        {'input': '999', 'inputType': 'octal', 'outputType': 'decimal'},  
        {'input': '', 'inputType': 'text', 'outputType': 'decimal'},
        {'input': None, 'inputType': 'binary', 'outputType': 'hexadecimal'},
        {'inputType': 'decimal', 'outputType': 'hexadecimal'},
    ]
)
def test_error_cases(client, payload):
    response = client.post('/convert', json=payload)
    data = response.get_json()
    assert data['result'] is None
    assert data['error'] is not None

# for running standalone:
if __name__ == "__main__":
    import pytest
    pytest.main()