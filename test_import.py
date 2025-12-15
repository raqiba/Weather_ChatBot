# test_import.py
try:
    from core.app import main
except Exception as e:
    import traceback
    traceback.print_exc()