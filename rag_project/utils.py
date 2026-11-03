import hashlib
def get_file_hash(path):
        with open(path,"rb") as file:
            text = file.read()
            hash_object = hashlib.sha256(text)
            file_hash = hash_object.hexdigest()
        return file_hash
