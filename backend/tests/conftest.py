import sys
from unittest.mock import MagicMock

# Mock sentence_transformers to run pytest without installing torch (532MB)
sys.modules['sentence_transformers'] = MagicMock()
