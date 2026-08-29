from Tools.saved_instruments.metadata_loader import load_model_metadata


_model = load_model_metadata("usb6525_gasValve", __file__)
globals().update(_model)
