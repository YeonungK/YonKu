from Tools.saved_instruments.metadata_loader import load_model_metadata


_model = load_model_metadata("INFICON_VGC401", __file__)
globals().update(_model)
