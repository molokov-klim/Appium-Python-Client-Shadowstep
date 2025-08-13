# shadowstep/utils/json_prepare.py
import json

my_dict = {'1012': '2023-08-25T23:02:00+03:00', '1018': '5010051677', '1020': 1.54, '1021': 'Автотестировщик И.', '1031': 1.54, '1037': '0000000001047959', '1038': 410, '1040': 5633, '1041': '9999078945337305', '1042': 2, '1054': 1, '1055': 1, '1059': [{'1023': 1, '1030': 'Товар', '1043': 0.77, '1079': 0.77, '1199': 6, '1212': 1}, {'1023': 1, '1030': 'Товар', '1043': 0.77, '1079': 0.77, '1199': 6, '1212': 1}], '1077': '31049967F4A9', '1081': 0, '1105': 1.54, '1209': 2, '1215': 0, '1216': 0, '1217': 0, 'fiscalDocumentType': 'receipt', 'qr': 't=20230825T2302&s=1.54&fn=9999078945337305&i=5633&fp=2573726889&n=1', 'short': False}


# Convert dictionary to JSON string with double quotes
json_str = json.dumps(my_dict, indent=2)
result = json_str.encode('utf-8').decode('unicode_escape')

# Pretty print JSON string with indentation
print(result)


