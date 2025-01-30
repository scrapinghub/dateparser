import fasttext
import numpy as np


class FastTextWrapper:
    def __init__(self, model_path):
        self.model = fasttext.load_model(model_path)

    def predict(self, text, k=1, threshold=0.0, on_unicode_error="strict"):
        def check(entry):
            if entry.find("\n") != -1:
                raise ValueError("predict processes one line at a time (remove '\\n')")
            entry += "\n"
            return entry

        if isinstance(text, list):
            text = [check(entry) for entry in text]
            all_labels, all_probs = self.model.f.multilinePredict(
                text, k, threshold, on_unicode_error
            )
            return all_labels, all_probs
        else:
            text = check(text)
            predictions = self.model.f.predict(text, k, threshold, on_unicode_error)
            if predictions:
                probs, labels = zip(*predictions)
            else:
                probs, labels = ([], ())

            # Using np.asarray(probs) to avoid errors in the test
            return labels, np.asarray(probs)


def load_model(model_path):
    return FastTextWrapper(model_path)
