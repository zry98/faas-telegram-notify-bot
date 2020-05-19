from time import time
from google.cloud import firestore

DB: firestore.Client = firestore.Client()


def log(log_type: str, data: dict, error_type: str = '') -> None:
    """Write log to the Firestore DB.

    Args:
        log_type (str): Type of log.
        data (dict): Data to write.
        error_type (str): Type of error if it's an error log.

    Returns:
        None

    """
    if log_type == 'error':
        doc_ref = DB.collection('notify-bot').document('error').collection(error_type).document(str(time()))
    else:
        doc_ref = DB.collection('notify-bot').document('archive').collection(log_type).document(str(time()))

    doc_ref.set(data)
