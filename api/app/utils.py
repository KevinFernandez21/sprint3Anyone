import hashlib
import os


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    # TODO: Implement the allowed_file function
    # Current implementation will return True for any file
    
    allowed_extensions = {".png", ".jpg", ".jpeg", ".gif"}
    if not filename:
        return False
    
    file_extension = os.path.splitext(filename)[1].lower()
# Check if the file extension of the filename received is in the set of allowed extensions (".png", ".jpg", ".jpeg", ".gif")
    return file_extension in allowed_extensions


async def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    # TODO: Implement the get_file_hash function
    # Current implementation will return the original file name.
    
    # Read file content and generate md5 hash (Check: https://docs.python.org/3/library/hashlib.html#hashlib.md5)
    if hasattr(file, 'read'):
        original_filename = file.filename

        if 'UploadFile'in str(type(file)):
            # It's an async UploadFile
            file_content = await file.read()
            await file.seek(0)
        else:
            # It's a sync FileStorage
            file_content = file.read()
            file.seek(0)

    elif isinstance(file, bytes):
        file_content = file
        original_filename = None
    else:
        original_filename = file
        with open(file, 'rb') as f:
            file_content = f.read()
    # Return file pointer to the beginning
    md5_hash = hashlib.md5(file_content).hexdigest()
    # Add original file extension
    if original_filename:
        file_extension = os.path.splitext(original_filename)[1]
        return md5_hash + file_extension
    else:
        return md5_hash


