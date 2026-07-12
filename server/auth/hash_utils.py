#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------
import bcrypt

#-----------------------------------------------------------------------
#                           Import Statements
#-----------------------------------------------------------------------

def hash_password(plain_password : str) -> str:
    """
        Hash a plain password into a Hash 
        Args:
            plain_password(str) : password need to convert into hash
        Returns:
            will give hashed password
    """
    hashed = bcrypt.hashpw(plain_password.encode("utf-8") , bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password : str , hashed_password : str) -> bool:
    """
        Verify the plain password against the hashed password
        Args:
            plain_password(str) : normal password
            hashed_password(str) : hashed password from the db
        Args:
            if they match return true else false
    """
    return bcrypt.checkpw(plain_password.encode("utf-8") , hashed_password.encode('utf-8'))