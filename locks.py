from multiprocessing import Lock

# Used to make database refreshing and updating atomic
database_lock = Lock()
