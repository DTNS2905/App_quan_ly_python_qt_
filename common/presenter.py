class Presenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model

    def close(self):
        self.model.close_connection()
