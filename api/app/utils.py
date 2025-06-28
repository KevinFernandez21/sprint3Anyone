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
    # Check if the file extension of the filename received is in the set of allowed extensions (".png", ".jpg", ".jpeg", ".gif")

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Check if the filename has an extension
    if '.' not in filename:
        return False
    
    # Extract the extension (convert to lowercase for case-insensitive comparison)
    extension = filename.rsplit('.', 1)[1].lower()
    
    # Check if the extension is in the allowed set
    return extension in allowed_extensions


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
    content = await file.read()
    
    # Generate MD5 hash from the content
    file_hash = hashlib.md5(content).hexdigest()
    
    # Reset file pointer to beginning for potential future use
    await file.seek(0)
    
    # Extract the original file extension (if exists)
    file_ext = os.path.splitext(file.filename)[-1].lower()
    new_filename = f'{file_hash}{file_ext}'

    return new_filename
