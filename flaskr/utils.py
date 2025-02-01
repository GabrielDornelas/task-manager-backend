from bson import json_util

def handle_collection_to_list(collection):
    """ Converte os dados da coleção para um formato manipulável """
    cursor = json_util.dumps(collection)
    cursor = cursor.replace('{"$oid": ', '')
    cursor = cursor.replace('"},', '",')
    cursor = cursor.replace('{"$date": ', '')
    cursor = cursor.replace('Z"}', 'Z"')
    cursor = cursor.replace('"}}', '"}')
    return json_util.loads(cursor)
