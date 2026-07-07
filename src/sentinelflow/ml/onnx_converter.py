"""
ONNX Model Converter for ultra-low latency inference (<100ms).

Converts Scikit-Learn (IsolationForest) and XGBoost models to ONNX format.
ONNX Runtime allows C++ level execution speed, significantly reducing the
Python overhead for real-time fraud detection.
"""

import os
from pathlib import Path
from loguru import logger
import pickle

try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    HAS_SKL2ONNX = True
except ImportError:
    HAS_SKL2ONNX = False

try:
    import onnxmltools
    from onnxmltools.convert import convert_xgboost
    from onnxconverter_common.data_types import FloatTensorType as XgbFloatTensorType
    HAS_ONNXMLTOOLS = True
except ImportError:
    HAS_ONNXMLTOOLS = False

def convert_isolation_forest_to_onnx(model_path: str, output_path: str, num_features: int = 21):
    """
    Convert a saved scikit-learn IsolationForest (and its Scaler) to ONNX.
    """
    if not HAS_SKL2ONNX:
        logger.error("skl2onnx is required to convert IsolationForest to ONNX.")
        return False

    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return False

    try:
        with open(model_path, "rb") as f:
            data = pickle.load(f)
        
        model = data.get("model")
        if not model:
            logger.error("No model found in pickle file.")
            return False

        # Define input type
        initial_type = [('float_input', FloatTensorType([None, num_features]))]
        
        # Convert model
        onx = convert_sklearn(model, initial_types=initial_type)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(onx.SerializeToString())
            
        logger.info(f"Successfully converted IsolationForest to ONNX: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to convert IsolationForest: {e}")
        return False

def convert_xgboost_to_onnx(model_path: str, output_path: str, num_features: int = 21):
    """
    Convert a saved XGBoost model to ONNX.
    """
    if not HAS_ONNXMLTOOLS:
        logger.error("onnxmltools is required to convert XGBoost to ONNX.")
        return False

    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return False

    try:
        with open(model_path, "rb") as f:
            data = pickle.load(f)
        
        model = data.get("model")
        if not model:
            logger.error("No model found in pickle file.")
            return False

        # Define input type
        initial_type = [('float_input', XgbFloatTensorType([None, num_features]))]
        
        # Convert model
        onx = convert_xgboost(model, initial_types=initial_type)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(onx.SerializeToString())
            
        logger.info(f"Successfully converted XGBoost to ONNX: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to convert XGBoost: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting ONNX Conversion process...")
    convert_isolation_forest_to_onnx("models/isolation_forest.pkl", "models/isolation_forest.onnx")
    convert_xgboost_to_onnx("models/xgboost_fraud.json", "models/xgboost_fraud.onnx")
